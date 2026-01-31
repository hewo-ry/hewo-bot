import nextcord
import datetime
import asyncio

from nextcord import EntityMetadata, Permissions, ScheduledEventEntityType, slash_command, TextChannel, ScheduledEventPrivacyLevel
from sqlmodel import Session
from nextcord.ext import commands, tasks
from google.oauth2 import service_account
from googleapiclient.discovery import build

from cogs import compare_events
from utils.config import settings, logger
from database import engine, session_lock
from database.utils import get_event_by_google_id, get_event_by_discord_id, get_calendars, get_calendar
from database.models import EventLink, Calendar as CalendarModel

class Calendar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.update_calendar.start()

    @slash_command(name="calendar", description="Calendar related commands", default_member_permissions=Permissions(administrator=True))
    async def calendar(self, interaction):
        pass

    @calendar.subcommand(name="update", description="Manually trigger a calendar update")
    async def manual_update_calendar(self, interaction):
        await interaction.response.send_message("Updating calendar...", ephemeral=True)
        await self.update_calendar()
        await interaction.followup.send("Calendar update complete.", ephemeral=True)

    @calendar.subcommand(name="add", description="Add a Google Calendar to sync with this server")
    async def add_calendar(self, interaction, google_id: str, channel_id: TextChannel | None = None):
        async with session_lock:
            with Session(engine) as session:
                db_calendar = get_calendar(session, google_id, interaction.guild.id)

                if db_calendar:
                    await interaction.response.send_message(f"Calendar `{google_id}` is already added.", ephemeral=True)
                    return

                new_calendar = CalendarModel(
                    google_id=google_id,
                    discord_id=interaction.guild.id,
                    channel_id=channel_id.id if channel_id else None
                )
                session.add(new_calendar)
                session.commit()

        await interaction.response.send_message(f"Added Google Calendar `{google_id}` to sync with this server.", ephemeral=True)

    @commands.Cog.listener()
    async def on_guild_scheduled_event_delete(self, event):
        async with session_lock:
            with Session(engine) as session:
                db_event = get_event_by_discord_id(session, event.id)
                if db_event:
                    session.delete(db_event)
                    session.commit()
                    logger.info(f"Deleted EventLink for Discord Event ID {event.id} as the event was deleted.")
    
    @tasks.loop(hours=1)
    async def update_calendar(self):
        creds = service_account.Credentials.from_service_account_file(
            settings.SERVICE_ACCOUNT_FILE,
            scopes=["https://www.googleapis.com/auth/calendar.readonly"],
        )

        events_to_update = []
        events_to_create = []

        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        async with session_lock:
            with Session(engine) as session:
                for calendar in get_calendars(session):
                    guild = self.bot.get_guild(calendar.discord_id)

                    # Skip if guild not found
                    if not guild:
                        continue

                    logger.info(f"Updating calendar for {guild.name}")

                    events_result = (
                        service.events()
                        .list(
                            calendarId=calendar.google_id,
                            timeMin=now,
                            maxResults=settings.NUM_TRACK_EVENTS,
                            singleEvents=True,
                            orderBy="startTime",
                        )
                        .execute()
                    )
                    google_events = events_result.get("items", [])

                    logger.info(f"Found {len(google_events)} events in Google Calendar")

                    for g_event in google_events:
                        event = get_event_by_google_id(session, g_event["id"])

                        update_obj = {
                            "google_event": g_event,
                            "db_event": event,
                            "discord_event": None
                        }

                        # Set event for update if found
                        if event:
                            d_event = guild.get_scheduled_event(event.discord_id)

                            update_obj["discord_event"] = d_event

                            if not d_event:
                                events_to_create.append(update_obj)
                                continue

                            # Check if there are changes
                            if not compare_events(g_event, d_event):
                                events_to_update.append(update_obj)

                        # Else set for creation
                        else:
                            events_to_create.append(update_obj)
                    
                    logger.info(f"Processing {len(events_to_update)} updates and {len(events_to_create)} creations")
                    
                    # Process updates
                    for event_data in events_to_update:
                        g_event = event_data["google_event"]
                        d_event = event_data["discord_event"]

                        if not d_event:
                            continue

                        start_time = datetime.datetime.fromisoformat(g_event["start"].get("dateTime", g_event["start"].get("date")))
                        end_time = datetime.datetime.fromisoformat(g_event["end"].get("dateTime", g_event["end"].get("date")))

                        try:
                            await d_event.edit(
                                name=g_event["summary"],
                                description=g_event.get("description", ""),
                                start_time=start_time,
                                end_time=end_time
                            )

                            event_data["db_event"].discord_id = d_event.id
                            session.add(event_data["db_event"])
                            session.commit()
                        except nextcord.Forbidden:
                            logger.warning(f"Missing permissions to edit event {d_event.id} in guild {guild.name}, probably modified manually.")

                    # Process creations
                    for event_data in events_to_create:
                        g_event = event_data["google_event"]
                        db_event = event_data["db_event"]

                        start_time = datetime.datetime.fromisoformat(g_event["start"].get("dateTime", g_event["start"].get("date")))
                        end_time = datetime.datetime.fromisoformat(g_event["end"].get("dateTime", g_event["end"].get("date")))

                        d_event = await guild.create_scheduled_event(
                            name=g_event["summary"],
                            description=g_event.get("description", ""),
                            start_time=start_time,
                            end_time=end_time,
                            metadata=EntityMetadata(location=g_event.get("location", "")),
                            entity_type=ScheduledEventEntityType.external,
                            privacy_level=ScheduledEventPrivacyLevel.guild_only,
                            reason="Syncing from Google Calendar"
                        )

                        # Save to database
                        if db_event:
                            db_event.discord_id = d_event.id
                        else:
                            db_event = EventLink(
                                google_id=g_event["id"],
                                discord_id=d_event.id
                            )
                        session.add(db_event)
                        session.commit()

                        await asyncio.sleep(1)  # To avoid hitting rate limits

                    logger.info(f"Calendar update for {guild.name} complete.")


    @update_calendar.before_loop
    async def before_update_calendar(self):
        await self.bot.wait_until_ready()
