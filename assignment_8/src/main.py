"""
FlyRank Internship · Backend Track · Week 7 · Assignment A8 / BE-08
PDF Report Generator API
"""

from fastapi import FastAPI
from src.routes import router as reports_router

app = FastAPI(
    title="PDF Report Generator API",
    version="1.0.0",
    description="Automated SQL query aggregation, HTML template rendering, and PDF report delivery service.",
)


@app.get("/health")
def health_check():
    """Liveness healthcheck endpoint."""
    return {"status": "ok"}


app.include_router(reports_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
