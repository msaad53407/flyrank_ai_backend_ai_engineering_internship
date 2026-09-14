"""
FlyRank Internship · Backend Track · Week 7 · Assignment A7 / BE-06
Your First Background Job - Application Entrypoint
"""

from fastapi import FastAPI
import inngest.fast_api

from src.functions import heartbeat, make_report, say_hello
from src.inngest_client import inngest_client
from src.routes import router as reports_router

app = FastAPI(
    title="Report Background Job API",
    version="1.0.0",
    description="FastAPI service demonstrating asynchronous durable background jobs with Inngest.",
)


@app.get("/health")
def health_check():
    """Healthcheck endpoint confirming API is running."""
    return {"status": "ok"}


# Include reports endpoints
app.include_router(reports_router)

# Mount Inngest handlers at /api/inngest for all 3 background functions
inngest.fast_api.serve(
    app,
    inngest_client,
    [say_hello, make_report, heartbeat],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
