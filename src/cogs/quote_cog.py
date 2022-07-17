"""Discord bot Quote cog."""

from datetime import datetime

import discord
from discord.ext import commands

from util import generate_logger, QuotesApi, CacheDict
from config import QUOTES_API_KEY

logger = generate_logger(__name__)


class QuoteCog(commands.Cog, name="Quote"):
    """Quote cog class."""

    def __init__(self, bot):
        self.bot = bot
        self.quote_embeds = CacheDict(10000)
        self.api = QuotesApi(QUOTES_API_KEY)

    def create_quote_embed(
        self, quote, author, tags, author_picture_url, channel
    ):  # pylint: disable=too-many-arguments, no-self-use
        """Creates an embed to display a quote."""
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.description = f"```📜 {quote}```"
        embed.set_thumbnail(url=author_picture_url)
        embed.add_field(name="Author", value=f"— *{author}*", inline=True)

        tags = ", ".join(tags)
        embed.add_field(name="Tags", value=f"{tags}", inline=True)

        if not isinstance(channel, discord.DMChannel):
            embed.set_footer(text="React with ❤️ to forward this quote to your inbox")

        embed.timestamp = datetime.utcnow()
        return embed

    def create_tag_list_embed(self, tags):
        """Creates an embed to display the tags available."""
        tag_names = ""

        for tag in sorted(tags):
            tag_names += f"{tag}\n"

        embed = discord.Embed(title="Quote Tags", colour=discord.Colour.blue())
        embed.description = tag_names

        embed.timestamp = datetime.utcnow()
        return embed

    def create_error_embed(self, message):
        """Creates an embed to display an error message."""
        embed = discord.Embed(colour=discord.Colour.red())
        embed.title = message
        return embed

    # Event Listeners
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Called when a message has a reaction added to it

        When a user reacts to a quote embedded by the bot with the proper reactions,
        it can be sent to him by using DM or it can be saved to their list of personal quotes,
        it all depends on the reaction used.
        """

        # Check that the reaction channels is not done on a private channel
        # and the user is not a bot
        if not isinstance(reaction.message.channel, discord.DMChannel) and not user.bot:

            if reaction.emoji == "❤️":
                # Get the ID from the message that was reacted to
                message_id = reaction.message.id

                # Check if the message that was reacted is a quote embed message
                if message_id in self.quote_embeds:
                    # Get the embed from the dictionary
                    embed = self.quote_embeds[message_id]

                    # Create a DM channel with the user to send the embed
                    await user.create_dm()
                    await user.dm_channel.send(embed=embed)

    # Class Methods
    async def cog_before_invoke(self, ctx):
        """A special method that acts as a cog local pre-invoke hook."""
        await ctx.trigger_typing()
        return await super().cog_before_invoke(ctx)

    async def cog_after_invoke(self, ctx):
        """A special method that acts as a cog local post-invoke hook."""
        return await super().cog_after_invoke(ctx)

    # Commands
    @commands.command(
        name="quote",
        aliases=["qt", "random"],
        brief="Sends a quote by author and/or tags.",
        help="Sends a quote by author and/or tags.",
    )
    async def quote(self, ctx, tags: str = None, *, author: str = None):
        """Sends a quote as a message."""
        try:
            # Get random quote filtered by tags and authors
            query_params = {}

            if tags is not None:
                query_params["tags"] = tags

            if author is not None:
                query_params["author"] = author

            quote = self.api.get_random_quote(query_params=query_params).json()

            embed = self.create_quote_embed(
                quote=quote["quote_text"],
                tags=quote["tags"],
                author=quote["author_name"],
                author_picture_url=quote["author_image"],
                channel=ctx.channel,
            )

            # Retrieve the message that was sent to the channels
            message = await ctx.channel.send(embed=embed)

            # If the command was not sent by DM, add an emoji to the message
            if not isinstance(ctx.channel, discord.DMChannel):
                await message.add_reaction("❤️")

                # Use dictionary as cache to keep track of quote embeds
                # for possible reactions
                embed = message.embeds[0]
                embed.set_footer(text=discord.Embed.Empty)
                embed.timestamp = discord.Embed.Empty
                self.quote_embeds[message.id] = embed

        except Exception:  # pylint: disable=broad-except
            logger.error("Sorry, could not get quote.")
            embed = self.create_error_embed("Sorry, could not find any quote.")
            await ctx.channel.send(embed=embed)

    @commands.command(
        name="tags",
        aliases=["tgs"],
        brief="Sends a list of all tags available.",
        help="Sends a list of all tags available.",
    )
    async def quote_tags(self, ctx):
        """Sends a list of all tags available."""
        try:
            # Get list of tags available from the api
            tags = self.api.get_all_tags().json()

            embed = self.create_tag_list_embed(list(tags["tags"]))
            await ctx.channel.send(embed=embed)

        except Exception:  # pylint: disable=broad-except
            logger.error("Could not get available tags")
            embed = self.create_error_embed("Sorry, could not get available tags.")
            await ctx.channel.send(embed=embed)


def setup(bot):
    """Sets up the quote cog for the bot."""
    logger.info("Loading Quote Cog")
    bot.add_cog(QuoteCog(bot))


def teardown(bot):
    """Tears down the quote cog for the bot."""
    logger.info("Unloading Quote Cog")
    bot.remove_cog("cogs.quote_cog")
