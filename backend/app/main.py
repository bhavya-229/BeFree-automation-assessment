"""FastAPI application initialization with CORS and error handlers."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.errors import ProcessingError
from app.api.v1.statements import router as statements_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ProcessingError)
async def processing_error_handler(request: Request, exc: ProcessingError):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_problem_dict(),
        media_type="application/problem+json",
    )


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": settings.VERSION}


@app.get("/api/v1/ready", tags=["Health"])
async def readiness_check():
    """Readiness probe."""
    return {"status": "ready"}


# Register API routers
app.include_router(statements_router, prefix=settings.API_V1_PREFIX)
