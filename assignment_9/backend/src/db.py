import json
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from src.config import DB_PATH
from src.models import WorkflowGraph, ExecutionRunResult


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS workflows (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            graph_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS executions (
            run_id TEXT PRIMARY KEY,
            workflow_id TEXT,
            input_context TEXT NOT NULL,
            status TEXT NOT NULL,
            result_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_workflow(workflow: WorkflowGraph) -> WorkflowGraph:
    init_db()
    conn = get_db()
    cursor = conn.cursor()
    now_iso = datetime.now().isoformat()

    if not workflow.id:
        workflow.id = f"wf-{str(uuid.uuid4())[:8]}"
        workflow.created_at = now_iso
    workflow.updated_at = now_iso

    graph_json = json.dumps(workflow.model_dump())

    cursor.execute(
        """
        INSERT INTO workflows (id, name, description, graph_json, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            description=excluded.description,
            graph_json=excluded.graph_json,
            updated_at=excluded.updated_at
        """,
        (
            workflow.id,
            workflow.name,
            workflow.description,
            graph_json,
            workflow.created_at or now_iso,
            workflow.updated_at,
        ),
    )
    conn.commit()
    conn.close()
    return workflow


def get_workflow(workflow_id: str) -> Optional[WorkflowGraph]:
    init_db()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT graph_json FROM workflows WHERE id = ?", (workflow_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    data = json.loads(row["graph_json"])
    return WorkflowGraph(**data)


def list_workflows() -> List[Dict]:
    init_db()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, created_at, updated_at FROM workflows ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_workflow(workflow_id: str) -> bool:
    init_db()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM workflows WHERE id = ?", (workflow_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def save_execution(result: ExecutionRunResult):
    init_db()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO executions (run_id, workflow_id, input_context, status, result_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(run_id) DO UPDATE SET
            status=excluded.status,
            result_json=excluded.result_json
        """,
        (
            result.run_id,
            result.workflow_id,
            result.input_context,
            result.status,
            json.dumps(result.model_dump()),
            result.created_at,
        ),
    )
    conn.commit()
    conn.close()


def get_execution(run_id: str) -> Optional[ExecutionRunResult]:
    init_db()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT result_json FROM executions WHERE run_id = ?", (run_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return ExecutionRunResult(**json.loads(row["result_json"]))


def list_executions(limit: int = 20) -> List[Dict]:
    init_db()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT run_id, workflow_id, status, created_at, result_json FROM executions ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        parsed = json.loads(r["result_json"])
        results.append({
            "run_id": r["run_id"],
            "workflow_id": r["workflow_id"],
            "status": r["status"],
            "created_at": r["created_at"],
            "path_length": len(parsed.get("path_taken", [])),
            "final_action": parsed.get("final_action"),
            "total_tokens": parsed.get("total_tokens", 0),
            "total_latency_ms": parsed.get("total_latency_ms", 0.0),
        })
    return results
