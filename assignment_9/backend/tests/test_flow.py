import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.templates import DEFAULT_TEMPLATES
from src.models import WorkflowGraph, Node, Edge, ExecuteRequest
from src.engine import run_workflow_engine, find_start_node, find_outgoing_edge

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_static_frontend():
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Decision Flow" in response.text


def test_templates_endpoints():
    response = client.get("/api/templates")
    assert response.status_code == 200
    templates = response.json()
    assert len(templates) >= 2
    assert any(t["id"] == "support-triage" for t in templates)

    # Get single template
    t_res = client.get("/api/templates/support-triage")
    assert t_res.status_code == 200
    wf = t_res.json()
    assert len(wf["nodes"]) >= 4
    assert len(wf["edges"]) >= 3


def test_engine_graph_traversal():
    template = DEFAULT_TEMPLATES["support-triage"]
    start_node = find_start_node(template)
    assert start_node is not None
    assert start_node.id == "node-1"

    # Outgoing edge resolution
    yes_edge = find_outgoing_edge(template.edges, "node-1", "YES")
    assert yes_edge is not None
    assert yes_edge.target == "node-2"

    no_edge = find_outgoing_edge(template.edges, "node-1", "NO")
    assert no_edge is not None
    assert no_edge.target == "node-3"


def test_workflow_crud():
    sample_wf = {
        "name": "Custom Test Flow",
        "description": "A quick test flow",
        "nodes": [
            {
                "id": "start-1",
                "type": "decisionNode",
                "position": {"x": 100, "y": 100},
                "data": {"label": "Is Test?", "prompt": "Is this a test?", "nodeType": "decision"},
            },
            {
                "id": "act-1",
                "type": "actionNode",
                "position": {"x": 100, "y": 250},
                "data": {"label": "Passed", "action": "Mark test pass", "nodeType": "action"},
            },
        ],
        "edges": [
            {"id": "e1", "source": "start-1", "target": "act-1", "sourceHandle": "yes", "label": "YES"}
        ],
    }

    # Save
    create_res = client.post("/api/workflows", json=sample_wf)
    assert create_res.status_code == 200
    saved = create_res.json()
    wf_id = saved["id"]
    assert wf_id.startswith("wf-")

    # Read
    read_res = client.get(f"/api/workflows/{wf_id}")
    assert read_res.status_code == 200
    assert read_res.json()["name"] == "Custom Test Flow"

    # List
    list_res = client.get("/api/workflows")
    assert list_res.status_code == 200
    assert any(w["id"] == wf_id for w in list_res.json())

    # Delete
    del_res = client.delete(f"/api/workflows/{wf_id}")
    assert del_res.status_code == 200

    # Read again -> 404
    read_again = client.get(f"/api/workflows/{wf_id}")
    assert read_again.status_code == 404


def test_execute_workflow_api():
    payload = {
        "workflow_id": "support-triage",
        "input_context": "Hi, I noticed an unauthorized charge of $199 on my Visa statement yesterday.",
    }

    response = client.post("/api/execute", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "completed"
    assert len(data["path_taken"]) >= 2
    assert "node-1" in data["path_taken"]
    assert len(data["node_results"]) >= 2
    # Verify first decision was YES (Billing inquiry)
    first_step = data["node_results"]["node-1"]
    assert first_step["decision"] in ("YES", "NO")

    # Verify execution history recorded
    hist_res = client.get("/api/executions")
    assert hist_res.status_code == 200
    assert len(hist_res.json()) >= 1
