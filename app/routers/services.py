"""Services API endpoints."""

from fastapi import APIRouter, Query

from app.config import get_settings
from app.models.services import Service, ServiceListResponse
from app.services import sheets_service


router = APIRouter()
settings = get_settings()


@router.get("", response_model=ServiceListResponse)
async def list_services(
    lang: str = Query(
        default=None,
        description="Filter by language (fr, en)",
    ),
    service_type: str | None = Query(None, description="Filter by service type"),
):
    """
    List all active church services.
    
    The services sheet has a language column to filter by language.
    """
    data = await sheets_service.get_services()
    
    # Filter to only active services (sheet uses 'is_active' column)
    data = [s for s in data if s.get("is_active", "").upper() == "TRUE"]
    
    # Filter by language if provided
    if lang:
        data = [s for s in data if s.get("language", "").lower() == lang.lower()]
    
    # Filter by service_type if provided
    if service_type:
        data = [s for s in data if s.get("service_type", "").lower() == service_type.lower()]
    
    # Sort by display_order
    data.sort(key=lambda x: int(x.get("display_order", "999") or "999"))
    
    services = [Service(**service) for service in data]
    return ServiceListResponse(services=services, total=len(services))
