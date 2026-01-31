import signal
import nextcord
from nextcord.ext import commands

from utils.config import settings, logger
from cogs.calendar import Calendar

def main():
    intents = nextcord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(
        command_prefix=commands.when_mentioned_or('!'),
        description="Hewo-bot",
        owner_id=int(settings.BOT_OWNER) if settings.BOT_OWNER else None,
        intents=intents
    )

    bot.add_cog(Calendar(bot))

    @bot.event
    async def on_ready():
        logger.info(f"\nLogged in as:\n{bot.user} (ID: {bot.user.id if bot.user else 'N/A'})")

    def handle_sigterm(sig, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, handle_sigterm)

    bot.run(settings.BOT_TOKEN)


if __name__ == "__main__":
    main()
