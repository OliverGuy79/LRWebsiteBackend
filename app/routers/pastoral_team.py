"""Pastoral Team API endpoints."""

from fastapi import APIRouter, Query

from app.models.pastoral_team import TeamMember, TeamListResponse
from app.services import sheets_service


router = APIRouter()


@router.get("", response_model=TeamListResponse)
async def list_team_members(
    role: str | None = Query(None, description="Filter by role"),
    preview: bool = Query(False, description="Include draft content for preview"),
):
    """List all published pastoral team members."""
    data = await sheets_service.get_pastoral_team()
    
    # Filter by status
    if preview:
        # Show published and draft (not archived)
        data = [m for m in data if m.get("status", "").lower() in ("published", "draft")]
    else:
        # Only show published
        data = [m for m in data if m.get("status", "").lower() == "published"]
    
    # Filter by role if provided
    if role:
        data = [m for m in data if m.get("role", "").lower() == role.lower()]
    
    # Sort by display_order
    data.sort(key=lambda x: int(x.get("display_order", "999") or "999"))
    
    team = [TeamMember(**member) for member in data]
    return TeamListResponse(team=team, total=len(team))
