"""
API route definitions for the report background job service.
"""

import asyncio
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
import inngest
from pydantic import BaseModel

from src.inngest_client import inngest_client
from src.storage import create_report, get_report, list_reports

router = APIRouter()


class CreateReportRequest(BaseModel):
    topic: Optional[str] = None


@router.post(
    "/reports",
    response_model=dict,
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_report(payload: CreateReportRequest):
    """
    Accept fast door:
    1. Validates presence of topic (400 if missing or blank).
    2. Saves report record as 'pending'.
    3. Emits 'report/requested' event to Inngest for background asynchronous processing.
    4. Immediately returns 202 Accepted with report id in milliseconds.
    """
    if not payload.topic or not payload.topic.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required field 'topic'. A valid topic is required to initiate a report.",
        )

    clean_topic = payload.topic.strip()
    record = create_report(clean_topic)

    # Dispatch event asynchronously so the HTTP response is instantaneous
    async def _send_event():
        try:
            await inngest_client.send(
                inngest.Event(
                    name="report/requested",
                    data={"id": record["id"], "topic": clean_topic},
                )
            )
        except Exception as e:
            # When Inngest Dev Server is offline (e.g. offline unit tests)
            print(f"[INNGEST DISPATCH] report/requested for id={record['id']}: {e}")

    asyncio.create_task(_send_event())

    return {"id": record["id"], "status": record["status"]}


@router.get("/reports/{report_id}", response_model=dict)
def get_report_status(report_id: str):
    """
    Status polling endpoint:
    Returns the report record. Initially 'pending', later 'done' or 'failed'.
    Returns 404 if report_id does not exist.
    """
    report = get_report(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with id '{report_id}' not found.",
        )
    return report


@router.get("/reports", response_model=List[dict])
def get_all_reports():
    """List all reports (Control panel dashboard extra)."""
    return list_reports()
