from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from routes.public import router as public_router
from routes.auth import router as auth_router
from routes.protected import router as protected_router
from config import PORT, ENVIRONMENT

app = FastAPI(
    title="FlyRank Auth API (Week 4 · BE-03 / A4)",
    description="Secure RESTful API demonstrating Supabase Auth, JWT verification, protected route middleware, and Swagger UI Bearer authorization.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Enable CORS for frontend clients / interactive testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Uniform error response format: {"error": "..."}
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail)}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_msg = errors[0]["msg"] if errors else "Invalid request body"
    field = ".".join(str(loc) for loc in errors[0]["loc"]) if errors else "body"
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": f"Validation error at {field}: {first_msg}"}
    )

# Register routes
app.include_router(public_router)
app.include_router(auth_router)
app.include_router(protected_router)

@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "FlyRank Auth API",
        "status": "healthy",
        "environment": ENVIRONMENT,
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Server running on port {PORT} and connected to Supabase Auth.")
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
