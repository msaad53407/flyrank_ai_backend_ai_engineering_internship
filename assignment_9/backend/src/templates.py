from typing import Dict, List
from src.models import WorkflowGraph, Node, Edge

DEFAULT_TEMPLATES: Dict[str, WorkflowGraph] = {
    "support-triage": WorkflowGraph(
        id="support-triage",
        name="Customer Support Triage",
        description="Classifies support tickets into billing, technical, or general inquiries with priority routing.",
        nodes=[
            Node(
                id="node-1",
                type="decisionNode",
                position={"x": 300, "y": 50},
                data={
                    "label": "Billing Inquiry?",
                    "prompt": "Is the user asking about billing, invoices, credit card charges, subscriptions, or payments?",
                    "nodeType": "decision",
                },
            ),
            Node(
                id="node-2",
                type="decisionNode",
                position={"x": 100, "y": 240},
                data={
                    "label": "Urgent / Double Charge?",
                    "prompt": "Is the user reporting an urgent double charge, unauthorized transaction, or severe billing error?",
                    "nodeType": "decision",
                },
            ),
            Node(
                id="node-3",
                type="decisionNode",
                position={"x": 520, "y": 240},
                data={
                    "label": "Technical Bug?",
                    "prompt": "Is the customer reporting a software bug, system crash, 500 error, or technical outage?",
                    "nodeType": "decision",
                },
            ),
            Node(
                id="action-urgent-billing",
                type="actionNode",
                position={"x": 20, "y": 440},
                data={
                    "label": "Priority Billing Escalation",
                    "action": "Route immediately to Senior Financial Support & notify Slack #urgent-billing",
                    "nodeType": "action",
                },
            ),
            Node(
                id="action-std-billing",
                type="actionNode",
                position={"x": 240, "y": 440},
                data={
                    "label": "Standard Billing Queue",
                    "action": "Assign ticket to Tier-1 Billing Specialist with standard 4-hour SLA",
                    "nodeType": "action",
                },
            ),
            Node(
                id="action-eng-bug",
                type="actionNode",
                position={"x": 440, "y": 440},
                data={
                    "label": "Engineering Bug Triage",
                    "action": "File Jira issue in Backlog and attach system diagnostic logs",
                    "nodeType": "action",
                },
            ),
            Node(
                id="action-general-faq",
                type="actionNode",
                position={"x": 660, "y": 440},
                data={
                    "label": "Knowledge Base Reply",
                    "action": "Send automated knowledge base self-serve link and general inquiry acknowledgement",
                    "nodeType": "action",
                },
            ),
        ],
        edges=[
            Edge(id="e1-2", source="node-1", target="node-2", sourceHandle="yes", label="YES"),
            Edge(id="e1-3", source="node-1", target="node-3", sourceHandle="no", label="NO"),
            Edge(id="e2-urgent", source="node-2", target="action-urgent-billing", sourceHandle="yes", label="YES"),
            Edge(id="e2-std", source="node-2", target="action-std-billing", sourceHandle="no", label="NO"),
            Edge(id="e3-eng", source="node-3", target="action-eng-bug", sourceHandle="yes", label="YES"),
            Edge(id="e3-gen", source="node-3", target="action-general-faq", sourceHandle="no", label="NO"),
        ],
    ),
    "sales-qualifier": WorkflowGraph(
        id="sales-qualifier",
        name="Enterprise Sales Lead Qualifier",
        description="Screens inbound sales inquiries for team size, urgency, and enterprise VIP treatment.",
        nodes=[
            Node(
                id="lead-node-1",
                type="decisionNode",
                position={"x": 300, "y": 50},
                data={
                    "label": "Enterprise Scale?",
                    "prompt": "Does the prospective customer mention an enterprise team size (>50 users) or corporate organization?",
                    "nodeType": "decision",
                },
            ),
            Node(
                id="lead-node-2",
                type="decisionNode",
                position={"x": 120, "y": 240},
                data={
                    "label": "Immediate Timeline?",
                    "prompt": "Does the lead have an active purchase timeframe within the next 30 days or immediate rollout need?",
                    "nodeType": "decision",
                },
            ),
            Node(
                id="lead-action-vip",
                type="actionNode",
                position={"x": 30, "y": 430},
                data={
                    "label": "Book Account Executive Demo",
                    "action": "Send Calendly VIP calendar link for 1-on-1 enterprise demo within 24h",
                    "nodeType": "action",
                },
            ),
            Node(
                id="lead-action-nurture",
                type="actionNode",
                position={"x": 260, "y": 430},
                data={
                    "label": "Enterprise Nurture Sequence",
                    "action": "Enroll lead in enterprise whitepaper and case study email drip",
                    "nodeType": "action",
                },
            ),
            Node(
                id="lead-action-starter",
                type="actionNode",
                position={"x": 520, "y": 240},
                data={
                    "label": "Self-Serve Starter Onboarding",
                    "action": "Direct lead to self-serve credit-card signup and sandbox tier",
                    "nodeType": "action",
                },
            ),
        ],
        edges=[
            Edge(id="le1-2", source="lead-node-1", target="lead-node-2", sourceHandle="yes", label="YES"),
            Edge(id="le1-starter", source="lead-node-1", target="lead-action-starter", sourceHandle="no", label="NO"),
            Edge(id="le2-vip", source="lead-node-2", target="lead-action-vip", sourceHandle="yes", label="YES"),
            Edge(id="le2-nurture", source="lead-node-2", target="lead-action-nurture", sourceHandle="no", label="NO"),
        ],
    ),
}


def get_template(template_id: str) -> WorkflowGraph:
    return DEFAULT_TEMPLATES.get(template_id, DEFAULT_TEMPLATES["support-triage"])


def list_templates() -> List[Dict]:
    return [
        {
            "id": k,
            "name": v.name,
            "description": v.description,
            "node_count": len(v.nodes),
            "edge_count": len(v.edges),
        }
        for k, v in DEFAULT_TEMPLATES.items()
    ]
