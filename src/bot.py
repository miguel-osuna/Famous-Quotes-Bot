import os
from os.path import dirname, abspath, join
from datetime import datetime

import discord
from discord.ext import commands

from util import generate_logger
from config import (
    SUPPORT_SERVER_INVITE_URL,
    BOT_INVITE_URL,
    DISCORD_TOKEN,
    COGS_PATH,
    BASE_PROJECT_PATH,
)

logger = generate_logger(__name__)


class FamousQuotesBot(commands.Bot):
    """ Discord Bot Client. """

    def __init__(self, cogs_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cogs_path = cogs_path

        # Load extensions when initialising the bot
        self.load_extensions()

    def load_extensions(self):
        for filename in os.listdir(self.cogs_path):
            if filename.endswith(".py"):
                extension = filename[:-3]
                try:
                    self.load_extension(f"cogs.{extension}")
                except Exception as e:
                    logger.error(f"Failed to load extension {extension}\n{e}")

    # Bot Evernt Listeners
    async def on_ready(self):
        """ Called when the client is done preparing the data received from Discord. """

        if not hasattr(self, "uptime"):
            self.uptime = datetime.utcnow()

        # Sets bots status and activity
        status = discord.Status.online
        activity = discord.Activity(
            name=f"{self.command_prefix}help", type=discord.ActivityType.listening
        )
        await self.change_presence(status=status, activity=activity, afk=False)

        logger.info(
            f"\nLogged in as '{self.user.name}'\n(id: {self.user.id})\nVersion: {discord.__version__}\n"
        )

    async def on_guild_join(self, guild):
        """ Called when a Guild is either created by the Client or when the Client joins a guild. """
        # Find the first text channel available

        # If general channel exists, create message
        support_server_invite_url = SUPPORT_SERVER_INVITE_URL

        greeting_message = f"""Hi there, I'm Famous Quotes Bot, thanks for adding me to your server.\n
                               To get started, use `~help` to check more information about me.\n
                               If you need help or find any error, join my support server at {support_server_invite_url} """

        # Embed message into general channel

    async def on_guild_remove(self, guild):
        """ Called when leaving or kicked from a discord server. """
        # Find the first text channel available

        # If general channel exists, create message
        bot_invite_url = BOT_INVITE_URL

        leave_message = f""" Thanks for adding Famous Quotes Bot to your server.\n
                            If you wish to add it again, use {bot_invite_url}\n
                            Have a nice day! """


if __name__ == "__main__":
    # Bot configuaration
    bot_description = """ Are you looking for a Quote? Famous Quotes Bot is here 
                          to the rescue!\nSearch quotes by author or genre with 
                          very simple commands."""

    command_prefix = "~"

    intents = discord.Intents.default()
    intents.members = True

    famous_quotes_bot = FamousQuotesBot(
        cogs_path=COGS_PATH,
        command_prefix=command_prefix,
        description=bot_description,
        intents=intents,
    )

    # Client event lop initialisation
    famous_quotes_bot.run(DISCORD_TOKEN)
