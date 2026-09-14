import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import inngest.fast_api

from src.config import inngest_client, STATIC_DIR
from src.inngest_flow import execute_decision_flow
from src.routes import router
from src.db import init_db

# Initialize SQLite database
init_db()

app = FastAPI(
    title="AI Decision Flow Service",
    description="Orchestrating visual AI decision graphs with React Flow + Inngest",
    version="1.0.0",
)

# Enable CORS for local Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Inngest endpoints at /api/inngest
inngest.fast_api.serve(
    app,
    inngest_client,
    [execute_decision_flow],
)

# Include API routes
app.include_router(router)

# Mount Static UI directory if built
if (STATIC_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

@app.get("/")
def serve_frontend_root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"status": "ok", "message": "AI Decision Flow API is active. Build frontend with `npm run build` in frontend directory."}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("src.main:app", host=host, port=port, reload=True)
