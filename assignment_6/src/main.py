"""
FlyRank Internship · Backend Track · Week 7 · Assignment A7 / BE-06
Your First Background Job
"""

from fastapi import FastAPI
import inngest.fast_api

from src.functions import say_hello
from src.inngest_client import inngest_client

app = FastAPI(
    title="Report Background Job API",
    version="1.0.0",
    description="FastAPI service demonstrating asynchronous durable background jobs with Inngest.",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


# Mount Inngest handlers at /api/inngest
inngest.fast_api.serve(
    app,
    inngest_client,
    [say_hello],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
