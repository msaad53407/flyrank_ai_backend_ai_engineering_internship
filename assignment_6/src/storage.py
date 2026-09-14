"""
In-memory report storage for background job execution and status tracking.
"""

import uuid
from typing import Dict, List, Optional

# In-memory dictionary tracking report state
reports: Dict[str, dict] = {}


def create_report(topic: str) -> dict:
    """Create and record a new pending report order."""
    report_id = str(uuid.uuid4())[:8]
    record = {
        "id": report_id,
        "topic": topic,
        "status": "pending",
        "result": None,
    }
    reports[report_id] = record
    return record


def get_report(report_id: str) -> Optional[dict]:
    """Retrieve report by unique ID."""
    return reports.get(report_id)


def list_reports() -> List[dict]:
    """List all reports (control panel extra)."""
    return list(reports.values())


def update_report(report_id: str, status: str, result: Optional[str] = None):
    """Update report lifecycle status and result payload."""
    if report_id in reports:
        reports[report_id]["status"] = status
        if result is not None:
            reports[report_id]["result"] = result


def get_counts() -> dict:
    """Return summary statistics of report states for heartbeat monitoring."""
    pending = sum(1 for r in reports.values() if r["status"] == "pending")
    done = sum(1 for r in reports.values() if r["status"] == "done")
    failed = sum(1 for r in reports.values() if r["status"] == "failed")
    return {
        "pending": pending,
        "done": done,
        "failed": failed,
        "total": len(reports),
    }
