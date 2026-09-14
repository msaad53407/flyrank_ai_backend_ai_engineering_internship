"""
FlyRank Internship · Backend Track · Week 7 · Assignment A7 / BE-06
Your First Background Job
"""

from fastapi import FastAPI

app = FastAPI(
    title="Report Background Job API",
    version="1.0.0",
    description="FastAPI service demonstrating asynchronous durable background jobs with Inngest.",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
