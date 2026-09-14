import inngest
import json
import uuid
from datetime import datetime
from src.config import inngest_client
from src.models import WorkflowGraph, Node, Edge, NodeStepResult, ExecutionRunResult
from src.engine import find_start_node, find_outgoing_edge
from src.llm import evaluate_decision_prompt
from src.db import save_execution, get_workflow


@inngest_client.create_function(
    fn_id="execute-decision-flow",
    trigger=inngest.TriggerEvent(event="decision-flow/run"),
)
async def execute_decision_flow(ctx: inngest.Context):
    """
    Inngest workflow executing the AI Decision Flow step-by-step:
    1. Reads workflow and input context from event data.
    2. Step-by-step executes each node via ctx.step.run.
    3. Evaluates prompt via LLM (strictly YES or NO).
    4. Follows matching edge to the next node.
    5. Persists execution trace and returns complete history.
    """
    event_data = ctx.event.data
    workflow_data = event_data.get("workflow")
    workflow_id = event_data.get("workflow_id")
    input_context = event_data.get("input_context", "")
    run_id = event_data.get("run_id") or f"run-{str(uuid.uuid4())[:8]}"

    if not workflow_data and workflow_id:
        wf_obj = get_workflow(workflow_id)
        if wf_obj:
            workflow_data = wf_obj.model_dump()

    if not workflow_data:
        err_res = ExecutionRunResult(
            run_id=run_id,
            workflow_id=workflow_id,
            status="failed",
            input_context=input_context,
            created_at=datetime.now().isoformat(),
            error="Workflow data not provided.",
        )
        save_execution(err_res)
        return err_res.model_dump()

    workflow = WorkflowGraph(**workflow_data)
    nodes_by_id = {n.id: n for n in workflow.nodes}
    start_node = find_start_node(workflow)

    if not start_node:
        err_res = ExecutionRunResult(
            run_id=run_id,
            workflow_id=workflow_id,
            status="failed",
            input_context=input_context,
            created_at=datetime.now().isoformat(),
            error="Graph contains no nodes to execute.",
        )
        save_execution(err_res)
        return err_res.model_dump()

    path_taken = []
    active_edges = []
    node_results = {}
    total_tokens = 0
    total_latency = 0.0
    final_action = None

    current_node_id = start_node.id
    max_steps = 30
    steps_count = 0

    while current_node_id and steps_count < max_steps:
        steps_count += 1
        current_node = nodes_by_id.get(current_node_id)
        if not current_node:
            break

        path_taken.append(current_node_id)
        step_id = f"step-{current_node_id}-{steps_count}"

        # Execute node via Inngest step
        async def run_step():
            node_type = current_node.type or "decisionNode"
            label = current_node.data.get("label", current_node.id)
            prompt = current_node.data.get("prompt")
            action = current_node.data.get("action")

            if node_type == "actionNode" or current_node.data.get("nodeType") == "action" or (action and not prompt):
                return {
                    "node_id": current_node.id,
                    "node_type": "action",
                    "label": label,
                    "prompt": None,
                    "decision": None,
                    "reasoning": f"Triggered action: {action or label}",
                    "chosen_edge_id": None,
                    "next_node_id": None,
                    "status": "completed",
                    "tokens": 0,
                    "latency_ms": 0.0,
                }

            eval_prompt = prompt or f"Should this item be approved for: {label}?"
            llm_res = evaluate_decision_prompt(eval_prompt, input_context)
            decision = llm_res["decision"]

            chosen_edge = find_outgoing_edge(workflow.edges, current_node.id, decision)
            next_id = chosen_edge.target if chosen_edge else None
            edge_id = chosen_edge.id if chosen_edge else None

            return {
                "node_id": current_node.id,
                "node_type": "decision",
                "label": label,
                "prompt": eval_prompt,
                "decision": decision,
                "reasoning": llm_res["reasoning"],
                "chosen_edge_id": edge_id,
                "next_node_id": next_id,
                "status": "completed",
                "tokens": llm_res["tokens"],
                "latency_ms": llm_res["latency_ms"],
            }

        step_output = await ctx.step.run(step_id, run_step)
        step_res = NodeStepResult(**step_output)
        node_results[current_node_id] = step_res

        total_tokens += step_res.tokens
        total_latency += step_res.latency_ms

        if step_res.chosen_edge_id:
            active_edges.append(step_res.chosen_edge_id)

        if step_res.node_type == "action":
            final_action = current_node.data.get("action") or current_node.data.get("label")

        current_node_id = step_res.next_node_id

    final_result = ExecutionRunResult(
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
        created_at=datetime.now().isoformat(),
    )

    # Persist in SQLite
    save_execution(final_result)
    return final_result.model_dump()
