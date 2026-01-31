from typing import Type
from sqlmodel import SQLModel, Session, col, select

from database.models import Calendar, EventLink

def get_all(session: Session, model: Type[SQLModel]):
    statement = select(model)
    results = session.exec(statement).all()
    return results

def get_event_by_google_id(session: Session, google_event_id: str):
    statement = select(EventLink).where(EventLink.google_id == google_event_id)
    result = session.exec(statement).first()
    return result

def get_event_by_discord_id(session: Session, discord_event_id: int):
    statement = select(EventLink).where(EventLink.discord_id == discord_event_id)
    result = session.exec(statement).first()
    return result

def get_calendars(session: Session):
    statement = select(Calendar)
    results = session.exec(statement).all()
    return results

def get_calendar(session: Session, google_id: str, discord_id: int):
    statement = select(Calendar).where(
        (Calendar.google_id == google_id) &
        (Calendar.discord_id == discord_id)
    )
    result = session.exec(statement).first()
    return result

def get_events_by_google_ids(session: Session, google_ids: list[str]):
    statement = select(EventLink).where(col(EventLink.google_id).in_(google_ids))
    results = session.exec(statement).all()
    return results

def get_events_by_discord_ids(session: Session, discord_ids: list[int]):
    statement = select(EventLink).where(col(EventLink.discord_id).in_(discord_ids))
    results = session.exec(statement).all()
    return results
