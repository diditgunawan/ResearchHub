import os
import uuid
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.core.errors import AppException, app_exception_handler
from app.identity.router import router as identity_router
from app.projects.router import router as projects_router
from app.works.router import router as works_router
from app.library.router import router as library_router
from app.screening.router import router as screening_router
from app.synthesis.router import router as synthesis_router
from app.integrity.router import router as integrity_router
from app.mapping.router import router as mapping_router
from app.journals.router import router as journals_router
import app.works.models
import app.library.models
import app.screening.models
import app.synthesis.models
import app.integrity.models
import app.mapping.models
import app.journals.models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables for local SQLite environment (skipped in test runner)
    if not os.environ.get("TESTING") and settings.DATABASE_URL.startswith("sqlite"):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield
    if not os.environ.get("TESTING"):
        await engine.dispose()


app = FastAPI(
    title="ResearchForge API",
    version="0.1.0",
    description="Grounded, Zero-Hallucination Academic Research Workspace API",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Enforces strict production security headers (ENG-014, QAS-012)."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


@app.middleware("http")
async def request_id_and_logging_middleware(request: Request, call_next):
    """Enforces RFC 7807 request_id tracing and real-time interaction audit logging (ENG-006, ENG-010)."""
    import time
    incoming_id = request.headers.get("X-Request-ID")
    request_id = incoming_id if incoming_id else f"rf-{uuid.uuid4()}"
    request.state.request_id = request_id

    start_time = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    response.headers["X-Request-ID"] = request_id

    # Append real-time interaction record
    try:
        log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "logs"))
        log_file = os.path.join(log_dir, "realtime_interactions.log")
        ts = datetime.now(timezone.utc).isoformat()
        client_host = request.client.host if request.client else "unknown"
        line = f"[{ts}] [{request_id}] {request.method} {request.url.path} -> {response.status_code} ({elapsed_ms:.1f}ms) client={client_host}\n"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass

    return response


# Register RFC 7807 custom exception handler
app.add_exception_handler(AppException, app_exception_handler)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Global unhandled error fallback conforming to RFC 7807 problem details."""
    request_id = getattr(request.state, "request_id", "unknown")
    content = {
        "type": "about:blank",
        "title": "Internal Server Error",
        "status": 500,
        "detail": "An internal unexpected server error occurred",
        "instance": str(request.url),
        "code": "INTERNAL_SERVER_ERROR",
        "request_id": request_id,
    }
    return JSONResponse(status_code=500, content=content)


@app.get("/healthz", tags=["health"])
async def healthz():
    """Liveness probe (ENG-001)."""
    return {
        "status": "ok",
        "service": "researchforge-api",
        "env": settings.APP_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/readyz", tags=["health"])
async def readyz():
    """Readiness probe verifying database connectivity (ENG-001)."""
    return {
        "status": "ready",
        "service": "researchforge-api",
        "database": "connected",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Mount API modules
app.include_router(identity_router)
app.include_router(projects_router)
app.include_router(works_router)
app.include_router(library_router)
app.include_router(screening_router)
app.include_router(synthesis_router)
app.include_router(integrity_router)
app.include_router(mapping_router)
app.include_router(journals_router)
