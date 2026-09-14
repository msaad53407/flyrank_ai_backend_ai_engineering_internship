"""
API routes for PDF report generation, status retrieval, and file delivery.
Implements:
- POST /reports with idempotency caching (Stage 4 & Stage 5)
- GET /reports/{id} status metadata (Stage 4)
- GET /reports/{id}/file streaming file download (Stage 4)
- GET /reports control panel listing (Extras)
"""

import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.config import DB_PATH, REPORTS_DIR
from src.queries import get_report_data
from src.renderer import generate_pdf_report

router = APIRouter()


class GenerateReportRequest(BaseModel):
    force: bool = False


@router.post(
    "/reports",
    response_model=dict,
)
async def generate_report_endpoint(payload: GenerateReportRequest = GenerateReportRequest()):
    """
    Generate report pipeline:
    1. Idempotency check: if report already exists for today and force is False,
       return existing id and link with HTTP 200.
    2. Otherwise, execute SQL queries -> compile HTML -> render PDF artifact ->
       record in reports table -> return HTTP 201.
    """
    today_prefix = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Idempotency Check (Stage 5)
    if not payload.force:
        cursor.execute(
            "SELECT id, path, created_at FROM reports WHERE created_at LIKE ? ORDER BY created_at DESC LIMIT 1",
            (f"{today_prefix}%",),
        )
        existing = cursor.fetchone()
        if existing and Path(existing["path"]).exists():
            conn.close()
            return Response(
                status_code=status.HTTP_200_OK,
                content=f'{{"id": "{existing["id"]}", "file": "/reports/{existing["id"]}/file", "cached": true}}',
                media_type="application/json",
            )

    # 1. Query: Execute SQL aggregations
    report_data = get_report_data(DB_PATH)

    # 2. Render: Build HTML and print to PDF artifact
    report_id = str(uuid.uuid4())[:8]
    pdf_filename = f"report-{today_prefix}-{report_id}.pdf"
    pdf_path = REPORTS_DIR / pdf_filename

    await generate_pdf_report(report_data, pdf_path)

    # 3. Store: Save metadata in database
    now_iso = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO reports (id, path, created_at) VALUES (?, ?, ?)",
        (report_id, str(pdf_path), now_iso),
    )
    conn.commit()
    conn.close()

    # 4. Return 201 Created with file link
    return Response(
        status_code=status.HTTP_201_CREATED,
        content=f'{{"id": "{report_id}", "file": "/reports/{report_id}/file"}}',
        media_type="application/json",
    )


@router.get("/reports/{report_id}", response_model=dict)
def get_report_metadata(report_id: str):
    """Retrieve metadata and file link for a generated report."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, path, created_at FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with id '{report_id}' not found.",
        )

    return {
        "id": row["id"],
        "file": f"/reports/{row['id']}/file",
        "created_at": row["created_at"],
    }


@router.get("/reports/{report_id}/file")
def download_report_file(report_id: str):
    """
    Serve the PDF artifact by link:
    Streams bytes directly from disk without holding entire payload in memory.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT path FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with id '{report_id}' not found.",
        )

    file_path = Path(row["path"])
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report PDF artifact file missing on disk.",
        )

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=file_path.name,
    )


@router.get("/reports", response_model=List[dict])
def list_all_reports():
    """Control panel: List all generated reports."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, path, created_at FROM reports ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": r["id"],
            "file": f"/reports/{r['id']}/file",
            "created_at": r["created_at"],
        }
        for r in rows
    ]
