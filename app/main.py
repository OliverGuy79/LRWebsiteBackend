"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
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

app = FastAPI(
    title="Église LaRencontre API",
    description="Backend API for the LaRencontre church website",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

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
