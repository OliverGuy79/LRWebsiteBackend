"""Events API endpoints."""

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, HTTPException, Query
import copy

from app.models.events import Event, EventFull, EventListResponse
from app.services import sheets_service, docs_service


router = APIRouter()

# Nombre de mois à générer pour les événements récurrents
RECURRING_MONTHS_AHEAD = 3


def parse_date(date_str: str | None) -> date | None:
    """Parse date string to date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_time(time_str: str | None) -> str | None:
    """Parse and format time string."""
    if not time_str:
        return None
    return time_str.strip()


def generate_recurring_instances(event: dict, months_ahead: int = RECURRING_MONTHS_AHEAD) -> list[dict]:
    """
    Generate recurring event instances based on recurrence pattern.

    Supported patterns:
    - "weekly" or "hebdomadaire": every week on the same day
    - "biweekly" or "bi-hebdomadaire": every 2 weeks
    - "monthly" or "mensuel": every month on the same day of month
    - "first_sunday": first Sunday of each month
    - "second_saturday": second Saturday of each month
    """
    instances = []

    # Check if event is recurring
    is_recurring = str(event.get("is_recurring", "")).lower() in ("true", "yes", "1", "oui")
    if not is_recurring:
        return [event]

    pattern = (event.get("recurrence_pattern") or "").lower().strip()
    if not pattern:
        return [event]

    # Parse start date
    start_date = parse_date(event.get("start_date"))
    if not start_date:
        return [event]

    # Calculate end date for generation (X months from today)
    today = date.today()
    generation_end = today + relativedelta(months=months_ahead)

    # Generate instances based on pattern
    current_date = start_date

    if pattern in ("weekly", "hebdomadaire"):
        # Start from today or the event start date, whichever is later
        if current_date < today:
            # Find the next occurrence
            days_ahead = (today - current_date).days
            weeks_ahead = (days_ahead // 7) + (1 if days_ahead % 7 > 0 else 0)
            current_date = current_date + timedelta(weeks=weeks_ahead)

        while current_date <= generation_end:
            instance = create_event_instance(event, current_date)
            instances.append(instance)
            current_date = current_date + timedelta(weeks=1)

    elif pattern in ("biweekly", "bi-hebdomadaire", "bi_weekly"):
        if current_date < today:
            days_ahead = (today - current_date).days
            weeks_ahead = (days_ahead // 14) + (1 if days_ahead % 14 > 0 else 0)
            current_date = current_date + timedelta(weeks=weeks_ahead * 2)

        while current_date <= generation_end:
            instance = create_event_instance(event, current_date)
            instances.append(instance)
            current_date = current_date + timedelta(weeks=2)

    elif pattern in ("monthly", "mensuel"):
        if current_date < today:
            # Move to next month
            while current_date < today:
                current_date = current_date + relativedelta(months=1)

        while current_date <= generation_end:
            instance = create_event_instance(event, current_date)
            instances.append(instance)
            current_date = current_date + relativedelta(months=1)

    elif pattern == "first_sunday":
        # Find first Sunday of each month
        current_month = today.replace(day=1)
        if current_date < today:
            current_month = today.replace(day=1)

        while True:
            # Find first Sunday of current_month
            first_sunday = current_month
            while first_sunday.weekday() != 6:  # 6 = Sunday
                first_sunday = first_sunday + timedelta(days=1)

            if first_sunday > generation_end:
                break
            if first_sunday >= today:
                instance = create_event_instance(event, first_sunday)
                instances.append(instance)

            current_month = current_month + relativedelta(months=1)

    elif pattern == "second_saturday":
        # Find second Saturday of each month
        current_month = today.replace(day=1)

        while True:
            # Find first Saturday of current_month
            first_saturday = current_month
            while first_saturday.weekday() != 5:  # 5 = Saturday
                first_saturday = first_saturday + timedelta(days=1)
            second_saturday = first_saturday + timedelta(weeks=1)

            if second_saturday > generation_end:
                break
            if second_saturday >= today:
                instance = create_event_instance(event, second_saturday)
                instances.append(instance)

            current_month = current_month + relativedelta(months=1)

    else:
        # Unknown pattern, return original event
        return [event]

    return instances if instances else [event]


def create_event_instance(parent_event: dict, instance_date: date) -> dict:
    """Create a new event instance for a specific date."""
    instance = copy.deepcopy(parent_event)

    # Generate unique ID based on parent ID and date
    instance["id"] = f"{parent_event.get('id', 'event')}_{instance_date.isoformat()}"

    # Update date
    instance["start_date"] = instance_date.isoformat()
    if parent_event.get("end_date"):
        # Keep the same duration if end_date was set
        original_start = parse_date(parent_event.get("start_date"))
        original_end = parse_date(parent_event.get("end_date"))
        if original_start and original_end:
            duration = original_end - original_start
            instance["end_date"] = (instance_date + duration).isoformat()

    # Mark as generated instance (not recurring itself)
    instance["is_recurring"] = "false"
    instance["parent_event_id"] = parent_event.get("id")

    return instance


def expand_recurring_events(events: list[dict], months_ahead: int = RECURRING_MONTHS_AHEAD) -> list[dict]:
    """Expand all recurring events into individual instances."""
    expanded = []
    for event in events:
        instances = generate_recurring_instances(event, months_ahead)
        expanded.extend(instances)
    return expanded


@router.get("", response_model=EventListResponse)
async def list_events(
    category: str | None = Query(None, description="Filter by category"),
    limit: int | None = Query(None, description="Limit number of results"),
    preview: bool = Query(False, description="Include draft content for preview"),
):
    """List all published events (with recurring events expanded)."""
    data = await sheets_service.get_events()

    # Filter by status
    if preview:
        # Show published and draft (not archived)
        data = [e for e in data if e.get("status", "").lower() in ("published", "draft")]
    else:
        # Only show published
        data = [e for e in data if e.get("status", "").lower() == "published"]

    # Filter by category if provided
    if category:
        data = [e for e in data if e.get("category", "").lower() == category.lower()]

    # Expand recurring events
    data = expand_recurring_events(data)

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
    preview: bool = Query(False, description="Include draft content for preview"),
):
    """List upcoming events (starting from today, with recurring events expanded)."""
    data = await sheets_service.get_events()

    today = date.today()

    # Filter by status
    if preview:
        # Show published and draft (not archived)
        data = [e for e in data if e.get("status", "").lower() in ("published", "draft")]
    else:
        # Only show published
        data = [e for e in data if e.get("status", "").lower() == "published"]

    # Expand recurring events
    data = expand_recurring_events(data)

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


@router.get("/{event_id}", response_model=EventFull)
async def get_event(
    event_id: str,
    preview: bool = Query(False, description="Allow viewing draft events"),
):
    """Get a single event by ID or slug, including full HTML content from Google Doc."""
    data = await sheets_service.get_events()
    data = expand_recurring_events(data)

    # Google Sheets peut contenir des espaces invisibles en fin de cellule.
    # Normaliser l'identifiant demandé et les valeurs avant la comparaison.
    normalized_event_id = event_id.strip()
    event_data = next((
        e for e in data
        if str(e.get("id", "")).strip() == normalized_event_id
        or str(e.get("slug", "")).strip() == normalized_event_id
    ), None)

    if not event_data:
        raise HTTPException(status_code=404, detail="Event not found")

    event_data = {
        **event_data,
        "id": str(event_data.get("id", "")).strip(),
        "slug": str(event_data.get("slug", "")).strip() or None,
        "title": str(event_data.get("title", "")).strip(),
    }

    # Check status - only allow published unless preview mode
    status = event_data.get("status", "").lower()
    if not preview and status != "published":
        raise HTTPException(status_code=404, detail="Event not found")

    # Fetch content from Google Doc if link is provided
    # `link` remains the canonical detailed-content document. Accept a Google
    # Docs URL in `media` as a backwards-compatible fallback, without treating
    # every media asset as article content.
    media_url = event_data.get("media") or ""
    doc_url = event_data.get("link") or (
        media_url if "docs.google.com/document" in media_url else None
    )
    content_html = await docs_service.get_article_content(doc_url)

    return EventFull(
        **event_data,
        content_html=content_html
    )
