from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Node(BaseModel):
    id: str
    type: Optional[str] = "decisionNode"
    position: Dict[str, float] = Field(default_factory=lambda: {"x": 0, "y": 0})
    data: Dict[str, Any] = Field(default_factory=dict)


class Edge(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: Optional[str] = None  # "yes" | "no"
    label: Optional[str] = None  # "YES" | "NO"
    animated: Optional[bool] = False
    data: Optional[Dict[str, Any]] = None


class WorkflowGraph(BaseModel):
    id: Optional[str] = None
    name: str = "AI Decision Workflow"
    description: Optional[str] = ""
    nodes: List[Node] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ExecuteRequest(BaseModel):
    workflow: Optional[WorkflowGraph] = None
    workflow_id: Optional[str] = None
    input_context: str = Field(..., description="Input query, support ticket, or customer message to evaluate")


class NodeStepResult(BaseModel):
    node_id: str
    node_type: str  # "decision" | "action" | "start"
    label: str
    prompt: Optional[str] = None
    decision: Optional[str] = None  # "YES" | "NO" | None
    reasoning: Optional[str] = None
    chosen_edge_id: Optional[str] = None
    next_node_id: Optional[str] = None
    status: str = "completed"  # "completed" | "failed" | "skipped"
    tokens: int = 0
    latency_ms: float = 0.0


class ExecutionRunResult(BaseModel):
    run_id: str
    workflow_id: Optional[str] = None
    status: str = "completed"  # "completed" | "failed"
    input_context: str
    path_taken: List[str] = Field(default_factory=list)
    active_edges: List[str] = Field(default_factory=list)
    node_results: Dict[str, NodeStepResult] = Field(default_factory=dict)
    final_action: Optional[str] = None
    total_tokens: int = 0
    total_latency_ms: float = 0.0
    created_at: str
    error: Optional[str] = None
