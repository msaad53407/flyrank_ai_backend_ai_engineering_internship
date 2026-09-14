import asyncio
import uuid
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from src.models import WorkflowGraph, ExecuteRequest, ExecutionRunResult
from src.db import (
    save_workflow,
    get_workflow,
    list_workflows,
    delete_workflow,
    save_execution,
    get_execution,
    list_executions,
)
from src.engine import run_workflow_engine
from src.templates import DEFAULT_TEMPLATES, list_templates, get_template
from src.config import inngest_client

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "service": "ai-decision-flow"}


# --- Templates ---
@router.get("/api/templates")
def get_templates_list():
    return list_templates()


@router.get("/api/templates/{template_id}")
def get_single_template(template_id: str):
    if template_id not in DEFAULT_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    return DEFAULT_TEMPLATES[template_id]


# --- Workflows CRUD ---
@router.get("/api/workflows")
def get_workflows():
    return list_workflows()


@router.post("/api/workflows")
def create_or_update_workflow(workflow: WorkflowGraph):
    saved = save_workflow(workflow)
    return saved


@router.get("/api/workflows/{workflow_id}")
def read_workflow(workflow_id: str):
    wf = get_workflow(workflow_id)
    if not wf:
        if workflow_id in DEFAULT_TEMPLATES:
            return DEFAULT_TEMPLATES[workflow_id]
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf


@router.delete("/api/workflows/{workflow_id}")
def remove_workflow(workflow_id: str):
    success = delete_workflow(workflow_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"deleted": True, "id": workflow_id}


# --- Execution Engine & Inngest ---
@router.post("/api/execute", response_model=ExecutionRunResult)
async def execute_workflow(payload: ExecuteRequest):
    """
    Executes an AI Decision Flow.
    Supports either an inline workflow or a workflow by workflow_id.
    Executes step-by-step, evaluating LLM decisions at each branch,
    and returns the full traversal path, active edges, and node results.
    """
    workflow = payload.workflow
    if not workflow and payload.workflow_id:
        workflow = get_workflow(payload.workflow_id)
        if not workflow and payload.workflow_id in DEFAULT_TEMPLATES:
            workflow = DEFAULT_TEMPLATES[payload.workflow_id]

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow definition or valid workflow_id must be provided.",
        )

    run_id = f"run-{str(uuid.uuid4())[:8]}"

    # Send non-blocking background event to Inngest for durability & tracking
    try:
        asyncio.create_task(
            inngest_client.send(
                inngest.Event(
                    name="decision-flow/run",
                    data={
                        "run_id": run_id,
                        "workflow": workflow.model_dump(),
                        "workflow_id": workflow.id,
                        "input_context": payload.input_context,
                    },
                )
            )
        )
    except Exception:
        # If Inngest event sender throws in disconnected dev mode, continue gracefully
        pass

    # Execute workflow graph engine and persist trace
    result = run_workflow_engine(workflow, payload.input_context, run_id=run_id)
    save_execution(result)
    return result


@router.get("/api/executions")
def get_execution_history():
    return list_executions()


@router.get("/api/executions/{run_id}")
def get_single_execution(run_id: str):
    res = get_execution(run_id)
    if not res:
        raise HTTPException(status_code=404, detail="Execution run not found")
    return res
