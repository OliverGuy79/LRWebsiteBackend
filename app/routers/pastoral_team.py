"""Pastoral Team API endpoints."""

from fastapi import APIRouter, Query

from app.models.pastoral_team import TeamMember, TeamListResponse
from app.services import sheets_service


router = APIRouter()


@router.get("", response_model=TeamListResponse)
async def list_team_members(
    role: str | None = Query(None, description="Filter by role"),
):
    """List all active pastoral team members."""
    data = await sheets_service.get_pastoral_team()
    
    # Filter to only active members (sheet uses 'is_active' column)
    data = [m for m in data if m.get("is_active", "").upper() == "TRUE"]
    
    # Filter by role if provided
    if role:
        data = [m for m in data if m.get("role", "").lower() == role.lower()]
    
    # Sort by display_order
    data.sort(key=lambda x: int(x.get("display_order", "999") or "999"))
    
    team = [TeamMember(**member) for member in data]
    return TeamListResponse(team=team, total=len(team))
