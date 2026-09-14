"""
FastAPI application entrypoint for Assignment 7 / BE-07.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.routes.triage import router as triage_router

app = FastAPI(
    title="Customer Support Message Triage API",
    version="1.0.0",
    description="FlyRank Internship Week 6 Assignment A17 / BE-07",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Format input validation errors as HTTP 400 naming the specific offending field.
    Ensures invalid payloads are rejected before incurring any LLM compute cost.
    """
    errors = exc.errors()
    field_name = "unknown"
    error_msg = "Invalid input"

    if errors:
        first_error = errors[0]
        loc = first_error.get("loc", [])
        # Extract field name from loc path, e.g. ('body', 'text') -> 'text'
        if len(loc) > 1:
            field_name = str(loc[1])
        elif len(loc) == 1:
            field_name = str(loc[0])
        error_msg = first_error.get("msg", "Validation error")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation failed",
            "field": field_name,
            "message": error_msg,
            "all_errors": errors,
        },
    )


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "triage-api"}


app.include_router(triage_router)
