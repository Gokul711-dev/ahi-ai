import os
import json
from datetime import datetime, timedelta
from utils.security import require_approval

# Path where the OAuth token will be stored (local, not shared)
_CALENDAR_TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "calendar_token.json")


def _ensure_token_file():
    """Internal helper to ensure the token file exists and is readable."""
    if not os.path.isfile(_CALENDAR_TOKEN_PATH):
        return None
    try:
        with open(_CALENDAR_TOKEN_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("token")
    except Exception:
        return None


def init_calendar(token: str) -> str:
    """Store a Google Calendar OAuth token for later API calls.

    The token is saved locally in a JSON file. The function requires user approval
    because it writes persistent credentials to disk.
    """
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(_CALENDAR_TOKEN_PATH), exist_ok=True)
    # Write the token atomically
    try:
        with open(_CALENDAR_TOKEN_PATH, "w", encoding="utf-8") as f:
            json.dump({"token": token}, f)
        return "Calendar token stored successfully."
    except Exception as e:
        return f"[Error] Failed to store calendar token: {e}"


def list_events(days: int = 7) -> str:
    """Return a mocked list of upcoming events for the next *days* days.

    In a full implementation this would call the Google Calendar API using the
    stored OAuth token. For now we return a static example to demonstrate the
    integration.
    """
    token = _ensure_token_file()
    if not token:
        return "[Error] No calendar token configured. Run `init_calendar` first."
    # Mocked events – in a real system you would query the API.
    today = datetime.utcnow().date()
    events = []
    for i in range(min(days, 3)):
        event_date = today + timedelta(days=i)
        events.append({
            "title": f"Sample Event {i + 1}",
            "start": f"{event_date}T09:00:00Z",
            "end": f"{event_date}T10:00:00Z",
        })
    # Format nicely
    lines = ["Upcoming Events:"]
    for ev in events:
        lines.append(f"- {ev['title']} from {ev['start']} to {ev['end']}")
    return "\n".join(lines)


def add_event(title: str, start: str, end: str) -> str:
    """Mock adding an event to the calendar.

    In a full implementation this would POST to the Google Calendar API. Here we
    simply acknowledge the request and return a success message.
    """
    token = _ensure_token_file()
    if not token:
        return "[Error] No calendar token configured. Run `init_calendar` first."
    # Basic validation of ISO‑8601 timestamps
    try:
        datetime.fromisoformat(start.replace('Z', '+00:00'))
        datetime.fromisoformat(end.replace('Z', '+00:00'))
    except Exception:
        return "[Error] Start/end times must be ISO‑8601 strings (e.g., 2024-01-01T09:00:00Z)."
    # Mock success
    return f"Event '{title}' scheduled from {start} to {end}."
