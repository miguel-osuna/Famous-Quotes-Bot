"""Discord bot client file."""

import os
from datetime import datetime

import discord
from discord.ext import commands

from util import generate_logger
from config import (
    SUPPORT_SERVER_INVITE_URL,
    BOT_INVITE_URL,
    DISCORD_TOKEN,
    COMMAND_PREFIX,
    COGS_PATH,
)

logger = generate_logger(__name__)


class FamousQuotesBot(commands.Bot):
    """Discord Bot Client."""

    def __init__(self, cogs_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cogs_path = cogs_path

        # Load extensions when initialising the bot
        self.load_extensions()

    def load_extensions(self):
        """Load bot cogs."""
        for filename in os.listdir(self.cogs_path):
            if filename.endswith(".py"):
                extension = filename[:-3]
                try:
                    self.load_extension(f"cogs.{extension}")
                except Exception as exc:  # pylint: disable=broad-except
                    logger.error("Failed to load extension %s\n%s", extension, exc)

    # Bot Evernt Listeners
    async def on_ready(self):
        """Called when the client is done preparing the data received from Discord."""

        if not hasattr(self, "uptime"):
            self.uptime = datetime.utcnow()

        # Sets bots status and activity
        status = discord.Status.online
        activity = discord.Activity(
            name=f"{self.command_prefix}help", type=discord.ActivityType.listening
        )
        await self.change_presence(status=status, activity=activity, afk=False)

        logger.info(
            "\nLogged in as '%s'\n" "(id: %s)\n" "Version: %s\n",
            self.user.name,
            self.user.id,
            discord.__version__,
        )

    async def on_guild_join(self, guild):
        """Called when a Guild is either created by the Client or when the Client joins a guild."""
        # Find the first text channel available

        # If general channel exists, create message
        greeting_message = (
            f"Hi there, I'm Famous Quotes Bot, thanks for adding me to your server.\n"
            f"To get started, use `~help` to check more information about me.\n"
            f"If you need help or find any error, "
            f"join my support server at {SUPPORT_SERVER_INVITE_URL}."
        )

        # Embed message into general channel

    async def on_guild_remove(self, guild):
        """Called when leaving or kicked from a discord server."""
        # Find the first text channel available

        # If general channel exists, create message
        leave_message = f""" Thanks for adding Famous Quotes Bot to your server.\n
                            If you wish to add it again, use {BOT_INVITE_URL}\n
                            Have a nice day! """


if __name__ == "__main__":
    # Bot configuaration
    BOT_DESCRIPTION = (
        "Are you looking for a Quote? Famous Quotes Bot is here "
        "to the rescue!\nSearch quotes by author or genre with "
        "very simple commands."
    )

    intents = discord.Intents.default()
    intents.members = True

    famous_quotes_bot = FamousQuotesBot(
        cogs_path=COGS_PATH,
        command_prefix=COMMAND_PREFIX,
        description=BOT_DESCRIPTION,
        intents=intents,
    )

    # Client event lop initialisation
    famous_quotes_bot.run(DISCORD_TOKEN)
