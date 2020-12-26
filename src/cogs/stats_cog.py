import os
from datetime import datetime

import discord
from discord.ext import commands, tasks

from util import generate_logger

logger = generate_logger(__name__)

BOT_INVITE_URL = os.getenv("BOT_INVITE_URL")
SUPPORT_SERVER_INVITE_URL = os.getenv("SUPPORT_SERVER_INVITE_URL")
VERSION = os.getenv("VERSION")


class StatsCog(commands.Cog, name="Stats"):
    """ Bot statistics cog. """

    def __init__(self, bot):
        self.bot = bot
        self.uptime = datetime.now()

    def get_time_difference(self, start_datetime, end_datetime):
        delta = end_datetime - start_datetime
        months, remainder = divmod(delta.seconds, 60 * 60 * 24 * 30)
        days, remainder = divmod(remainder, 60 * 60 * 24)
        hours, remainder = divmod(remainder, 60 * 60)
        minutes, remainder = divmod(remainder, 60)
        seconds = remainder

        time_difference = "**{}** *months*, **{}** *days*, **{}** *hours*, **{}** *minutes*, **{}** *seconds*".format(
            months, days, hours, minutes, seconds
        )

        return time_difference

    def create_uptime_embed(self, start_datetime):
        """ Creates an embed to show the total uptime of the bot. """
        # Create the uptime string
        end_datetime = datetime.utcnow()
        uptime_string = self.get_time_difference(start_datetime, end_datetime)

        # Create uptime embed
        embed = discord.Embed(
            title="⏱️ Famous Quotes Bot Uptime", color=discord.Color.dark_magenta()
        )
        embed.description = f"\n\n{uptime_string}"
        embed.timestamp = end_datetime

        return embed

    def create_about_embed(
        self,
        server_invite_url,
        members,
        servers,
        channels,
        commands,
        version,
        start_datetime,
    ):
        """ Creates an embed to show information about the bot. """
        embed = discord.Embed(color=discord.Color.dark_magenta())
        embed.title = "🤖 Official Famous Quotes Bot Server Invite"
        embed.url = server_invite_url
        embed.description = "Famous Quotes Bot is a bot that provides famous quotes by author, category or random."

        end_datetime = datetime.utcnow()
        uptime_string = self.get_time_difference(start_datetime, end_datetime)
        uptime_string = uptime_string.replace(", ", "\n")

        # Create about embed
        embed.add_field(name="👥 Members", value=f"**{members}** in total", inline=True)
        embed.add_field(name="🖥️ Servers", value=f"**{servers}** in total", inline=True)
        embed.add_field(
            name="🌐 Channels", value=f"**{channels}** in total", inline=True
        )
        embed.add_field(name="❓ Status", value="Online", inline=True)
        embed.add_field(name="⏱️ Uptime", value=f"{uptime_string}", inline=True)
        embed.add_field(
            name="⚙️ Commands", value=f"**{commands}** in total", inline=True
        )

        embed.set_footer(text=f"Famous Quotes Bot {version}")
        embed.timestamp = end_datetime
        return embed

    def create_version_embed(self, version):
        """ Creates an embed to show the bots version. """
        embed = discord.Embed(color=discord.Color.dark_magenta())
        embed.title = f"Famous Quotes Bot `{version}`"
        embed.timestamp = datetime.utcnow()
        return embed

    def create_join_embed(self, version, bot_invite_url, server_invite_url):
        """ Creates an embed that includes a bot invitation to a server. """
        embed = discord.Embed(color=discord.Color.dark_magenta())
        embed.title = "🤖 Add Famous Quotes Bot to your Discord Server!"
        embed.description = "If you're interested in adding Famous Quotes Bot to your server, you'll find some links below to help you get started."
        embed.add_field(
            name="Famous Bot Invite", value=f"{bot_invite_url}", inline=False
        )
        embed.add_field(
            name="Famous Quotes Bot Support Server",
            value=f"{server_invite_url}",
            inline=False,
        )
        embed.set_footer(text=f"Famous Quotes Bot {version}")
        embed.timestamp = datetime.utcnow()
        return embed

    # Class Methods
    async def cog_before_invoke(self, ctx):
        """ A special method that acts as a cog local pre-invoke hook. """
        await ctx.trigger_typing()
        return await super().cog_before_invoke(ctx)

    async def cog_after_invoke(self, ctx):
        """ A special method that acts as a cog local post-invoke hook. """
        return await super().cog_after_invoke(ctx)

    # Commands
    @commands.command(name="uptime", help="Check the bots uptime")
    async def uptime(self, ctx):
        """ Tells how long the bot has been up for. """
        start_datetime = datetime(2020, 12, 25)

        embed = self.create_uptime_embed(start_datetime)
        await ctx.send(embed=embed)

    @commands.command(name="about", help="Tells information about the bot itself.")
    async def about(self, ctx):
        """ Tells you information about the bot itself. """
        # Embed variables
        version = VERSION
        start_datetime = datetime(2020, 12, 25)
        server_invite_url = SUPPORT_SERVER_INVITE_URL
        total_members = len(self.bot.users)
        commands = len(self.bot.commands)

        guilds = 0
        text_channels = 0
        # Get every text channel from every guild the bot is in
        for guild in self.bot.guilds:
            guilds += 1
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    text_channels += 1

        # Create embed
        embed = self.create_about_embed(
            server_invite_url,
            total_members,
            guilds,
            text_channels,
            commands,
            version,
            start_datetime,
        )
        await ctx.send(embed=embed)

    @commands.command(name="version", help="Tells the version of the bot.")
    async def version(self, ctx):
        """ Tells the version of the bot. """
        # Get bot version
        version = VERSION
        embed = self.create_version_embed(version)
        await ctx.send(embed=embed)

    @commands.command(
        name="join",
        aliases=["invite"],
        help="Sends a link to add Famous Quotes Bot to your server.",
    )
    async def join(self, ctx):
        """ Sends a link to add Famous Quotes Bot to your server. """
        version = VERSION
        bot_invite_url = BOT_INVITE_URL
        server_invite_url = SUPPORT_SERVER_INVITE_URL
        embed = self.create_join_embed(version, bot_invite_url, server_invite_url)
        await ctx.send(embed=embed)


def setup(bot):
    """ Sets up the stats cog for the bot. """
    logger.info("Loading Stats Cog")
    bot.add_cog(StatsCog(bot))


def teardown(bot):
    """ Tears down the stats cog for the bot. """
    logger.info("Unloading Stats Cog")
    bot.remove_cog("stats_cog")
