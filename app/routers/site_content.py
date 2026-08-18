"""Site Content API endpoints."""

from fastapi import APIRouter, HTTPException, Query

from app.models.site_content import SiteContentItem, SiteContentResponse
from app.services import sheets_service


router = APIRouter()


@router.get("", response_model=SiteContentResponse)
async def list_site_content(
    key: str | None = Query(None, description="Filter by content key"),
):
    """List all site content entries."""
    data = await sheets_service.get_site_content()

    # Filter by key if provided
    if key:
        data = [item for item in data if item.get("key", "").lower() == key.lower()]

    items = [SiteContentItem(**item) for item in data]
    return SiteContentResponse(items=items, total=len(items))


@router.get("/{item_id}", response_model=SiteContentItem)
async def get_site_content_item(
    item_id: str,
):
    """Get a single site content entry by ID or key."""
    data = await sheets_service.get_site_content()

    item = next(
        (i for i in data if i.get("id") == item_id or i.get("key") == item_id),
        None,
    )

    if not item:
        raise HTTPException(status_code=404, detail="Site content not found")

    return SiteContentItem(**item)
