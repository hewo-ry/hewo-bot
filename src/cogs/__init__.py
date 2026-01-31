import datetime

from nextcord.scheduled_events import ScheduledEvent

def compare_events(g_event: dict, d_event: ScheduledEvent):
    isSame = True
    isSame = isSame and (d_event.name == g_event["summary"])
    isSame = isSame and (d_event.description == g_event.get("description", ""))
    start_time = datetime.datetime.fromisoformat(g_event["start"].get("dateTime", g_event["start"].get("date")))
    end_time = datetime.datetime.fromisoformat(g_event["end"].get("dateTime", g_event["end"].get("date")))
    isSame = isSame and (d_event.start_time == start_time)
    isSame = isSame and (d_event.end_time == end_time)

    return isSame
