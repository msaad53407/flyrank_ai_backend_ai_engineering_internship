import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from src.models import WorkflowGraph, Node, Edge, NodeStepResult, ExecutionRunResult
from src.llm import evaluate_decision_prompt


def find_start_node(workflow: WorkflowGraph) -> Optional[Node]:
    """
    Identifies the entrypoint node of the graph.
    Prefers node with type 'startNode' or 'start', then node with 0 incoming edges.
    """
    if not workflow.nodes:
        return None

    # Check explicit start node
    for n in workflow.nodes:
        if n.type in ("startNode", "start") or n.data.get("nodeType") == "start":
            return n

    # Find nodes with no incoming edges
    target_ids = {e.target for e in workflow.edges}
    candidate_roots = [n for n in workflow.nodes if n.id not in target_ids]
    if candidate_roots:
        return candidate_roots[0]

    return workflow.nodes[0]


def find_outgoing_edge(
    edges: List[Edge], source_id: str, decision: Optional[str]
) -> Optional[Edge]:
    """
    Finds the outgoing edge from source_id corresponding to the given decision (YES or NO).
    """
    source_edges = [e for e in edges if e.source == source_id]
    if not source_edges:
        return None

    if decision is None:
        return source_edges[0]

    dec_upper = decision.upper()
    for e in source_edges:
        handle = (e.sourceHandle or "").lower()
        lbl = (e.label or "").upper()
        if dec_upper == "YES" and (handle == "yes" or lbl == "YES" or "yes" in lbl.lower()):
            return e
        if dec_upper == "NO" and (handle == "no" or lbl == "NO" or "no" in lbl.lower()):
            return e

    # Fallback to first available edge
    return source_edges[0]


def execute_graph_step(
    node: Node,
    edges: List[Edge],
    input_context: str,
) -> Tuple[NodeStepResult, Optional[str]]:
    """
    Executes a single node in the graph and determines the next node ID.
    """
    node_type = node.type or "decisionNode"
    label = node.data.get("label", node.id)
    prompt = node.data.get("prompt")
    action = node.data.get("action")

    # If it is an action / terminal node
    if node_type == "actionNode" or node.data.get("nodeType") == "action" or (action and not prompt):
        return NodeStepResult(
            node_id=node.id,
            node_type="action",
            label=label,
            prompt=None,
            decision=None,
            reasoning=f"Triggered action: {action or label}",
            chosen_edge_id=None,
            next_node_id=None,
            status="completed",
            tokens=0,
            latency_ms=0.0,
        ), None

    # It is a decision node
    eval_prompt = prompt or f"Should this item be approved for: {label}?"
    llm_res = evaluate_decision_prompt(eval_prompt, input_context)
    decision = llm_res["decision"]

    chosen_edge = find_outgoing_edge(edges, node.id, decision)
    next_node_id = chosen_edge.target if chosen_edge else None
    chosen_edge_id = chosen_edge.id if chosen_edge else None

    step_result = NodeStepResult(
        node_id=node.id,
        node_type="decision",
        label=label,
        prompt=eval_prompt,
        decision=decision,
        reasoning=llm_res["reasoning"],
        chosen_edge_id=chosen_edge_id,
        next_node_id=next_node_id,
        status="completed",
        tokens=llm_res["tokens"],
        latency_ms=llm_res["latency_ms"],
    )

    return step_result, next_node_id


def run_workflow_engine(
    workflow: WorkflowGraph,
    input_context: str,
    run_id: Optional[str] = None,
) -> ExecutionRunResult:
    """
    Complete in-process execution of the workflow graph.
    Used for direct execution and automated test validation.
    """
    run_id = run_id or f"run-{str(uuid.uuid4())[:8]}"
    now_iso = datetime.now().isoformat()

    nodes_by_id = {n.id: n for n in workflow.nodes}
    start_node = find_start_node(workflow)

    if not start_node:
        return ExecutionRunResult(
            run_id=run_id,
            workflow_id=workflow.id,
            status="failed",
            input_context=input_context,
            created_at=now_iso,
            error="Graph contains no nodes to execute.",
        )

    path_taken: List[str] = []
    active_edges: List[str] = []
    node_results: Dict[str, NodeStepResult] = {}
    total_tokens = 0
    total_latency = 0.0
    final_action = None

    current_node_id: Optional[str] = start_node.id
    max_steps = 30
    steps_count = 0

    while current_node_id and steps_count < max_steps:
        steps_count += 1
        current_node = nodes_by_id.get(current_node_id)
        if not current_node:
            break

        path_taken.append(current_node_id)
        step_res, next_node_id = execute_graph_step(current_node, workflow.edges, input_context)
        node_results[current_node_id] = step_res

        total_tokens += step_res.tokens
        total_latency += step_res.latency_ms

        if step_res.chosen_edge_id:
            active_edges.append(step_res.chosen_edge_id)

        if step_res.node_type == "action":
            final_action = current_node.data.get("action") or current_node.data.get("label")

        current_node_id = next_node_id

    return ExecutionRunResult(
        run_id=run_id,
        workflow_id=workflow.id,
        status="completed",
        input_context=input_context,
        path_taken=path_taken,
        active_edges=active_edges,
        node_results=node_results,
        final_action=final_action,
        total_tokens=total_tokens,
        total_latency_ms=round(total_latency, 2),
        created_at=now_iso,
    )
