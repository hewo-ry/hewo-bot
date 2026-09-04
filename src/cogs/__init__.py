import datetime

from nextcord.scheduled_events import ScheduledEvent

def parse_google_time(time_obj: dict) -> datetime.datetime:
    """Parse a Google Calendar start/end object, assuming UTC for date-only (all-day) values which are naive."""
    dt = datetime.datetime.fromisoformat(time_obj.get("dateTime", time_obj.get("date")))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt

def compare_events(g_event: dict, d_event: ScheduledEvent):
    isSame = True
    isSame = isSame and (d_event.name == g_event["summary"])
    isSame = isSame and (d_event.description == g_event.get("description", ""))
    start_time = parse_google_time(g_event["start"])
    end_time = parse_google_time(g_event["end"])
    isSame = isSame and (d_event.start_time == start_time)
    isSame = isSame and (d_event.end_time == end_time)

    return isSame
