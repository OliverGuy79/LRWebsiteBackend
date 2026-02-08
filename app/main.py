"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time

from app.config import get_settings
from app.logging_config import setup_logging, get_logger
from app.routers import (
    articles,
    boutique,
    church_info,
    events,
    home_groups,
    pastoral_team,
    services,
    vision,
)

settings = get_settings()

# Setup structured logging
setup_logging(
    level=settings.log_level,
    json_format=settings.log_json_format,
    app_name="lr-website-backend"
)

logger = get_logger(__name__)

# Initialize rate limiter
# Default: 60 requests per minute per IP
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Église LaRencontre API", extra={
        "version": "0.1.0",
        "log_level": settings.log_level,
        "rate_limit": "60/minute",
    })
    yield
    logger.info("Shutting down Église LaRencontre API")


app = FastAPI(
    title="Église LaRencontre API",
    description="Backend API for the LaRencontre church website",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Register rate limiter with app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with timing."""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000
    
    # Log request (skip health checks to reduce noise)
    if request.url.path != "/api/health":
        logger.info(
            f"{request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query": str(request.query_params),
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            }
        )
    
    return response


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(articles.router, prefix="/api/articles", tags=["Articles"])
app.include_router(boutique.router, prefix="/api/boutique", tags=["Boutique"])
app.include_router(church_info.router, prefix="/api/church-info", tags=["Church Info"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(home_groups.router, prefix="/api/home-groups", tags=["Home Groups"])
app.include_router(pastoral_team.router, prefix="/api/pastoral-team", tags=["Pastoral Team"])
app.include_router(services.router, prefix="/api/services", tags=["Services"])
app.include_router(vision.router, prefix="/api/vision", tags=["Vision"])


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "lr-website-backend"}
