"""Events API endpoints."""

from datetime import datetime, date
from fastapi import APIRouter, HTTPException, Query

from app.models.events import Event, EventListResponse
from app.services import sheets_service


router = APIRouter()


def parse_date(date_str: str | None) -> date | None:
    """Parse date string to date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


@router.get("", response_model=EventListResponse)
async def list_events(
    category: str | None = Query(None, description="Filter by category"),
    limit: int | None = Query(None, description="Limit number of results"),
):
    """List all published events."""
    data = await sheets_service.get_events()
    
    # Filter to only published events
    data = [e for e in data if e.get("is_published", "").upper() == "TRUE"]
    
    # Filter by category if provided
    if category:
        data = [e for e in data if e.get("category", "").lower() == category.lower()]
    
    # Sort by start_date
    data.sort(key=lambda x: x.get("start_date", ""))
    
    # Limit if specified
    if limit:
        data = data[:limit]
    
    events = [Event(**event) for event in data]
    return EventListResponse(events=events, total=len(events))


@router.get("/upcoming", response_model=EventListResponse)
async def list_upcoming_events(
    limit: int = Query(5, description="Number of events to return"),
):
    """List upcoming events (starting from today)."""
    data = await sheets_service.get_events()
    
    today = date.today()
    
    # Filter to only published events
    data = [e for e in data if e.get("is_published", "").upper() == "TRUE"]
    
    # Filter to only future events
    upcoming = []
    for event in data:
        event_date = parse_date(event.get("start_date"))
        if event_date and event_date >= today:
            upcoming.append(event)
    
    # Sort by start_date
    upcoming.sort(key=lambda x: x.get("start_date", ""))
    
    # Limit results
    upcoming = upcoming[:limit]
    
    events = [Event(**event) for event in upcoming]
    return EventListResponse(events=events, total=len(events))


@router.get("/{event_id}", response_model=Event)
async def get_event(event_id: str):
    """Get a single event by ID."""
    data = await sheets_service.get_events()
    
    event_data = next((e for e in data if e.get("id") == event_id), None)
    
    if not event_data:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return Event(**event_data)
