import os
from datetime import datetime

import discord
from discord.ext import commands, tasks

from util import generate_logger, Pages, QuotesApi, CacheDict

logger = generate_logger(__name__)

QUOTES_API_KEY = os.getenv("QUOTES_API_KEY")


class QuotesPaginator(Pages):
    pass


class QuoteAuthorsPaginator(Pages):
    pass


class QuoteDetectPaginator(Pages):
    pass


class QuoteCog(commands.Cog, name="Quote"):
    def __init__(self, bot):
        self.bot = bot
        self.quote_embeds = CacheDict(1000)
        self.api = QuotesApi(QUOTES_API_KEY)

    def create_quote_embed(self, quote, author, tags, author_picture_url, channel):
        """ Creates an embed to display a quote. """
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.description = f"```📜 {quote}```"
        embed.set_thumbnail(url=author_picture_url)
        embed.add_field(name="Author", value=f"— *{author}*", inline=True)

        tags = ", ".join(tags)
        embed.add_field(name="Tags", value=f"{tags}", inline=True)

        if not isinstance(channel, discord.DMChannel):
            embed.set_footer(text="React with ❤️ to forward this quote to your inbox")

        # Add timestamp to the embed
        embed.timestamp = datetime.utcnow()
        return embed

    def create_quote_list_embed(self, author_quote_list, channel):
        """ Creates an embed to display a list of quotes. """

        embed = discord.Embed(colour=discord.Colour.blue())

        for author_dict in author_quote_list:
            quote_entries = ""
            author_name = author_dict["name"]

            for author_quote in author_dict["quote_list"]:
                quote_entries += "📜 {} ({})\n\n".format(
                    author_quote["quote"], author_quote["category"]
                )

            # Add author and its quotes
            embed.add_field(
                name=f"*{author_name}*", value=f"```{quote_entries}```", inline=False,
            )

        if not isinstance(channel, discord.DMChannel):
            embed.set_footer(text="React with ❤️ to forward this quote to your inbox.")

        # Add timestamp to the embed
        embed.timestamp = datetime.utcnow()

        return embed

    def create_tag_list_embed(self, tags):
        """ Creates an embed to display the categories available. """
        tag_names = ""

        for tag in tags:
            tag_names += "{}\n".format(tag["name"])

        embed = discord.Embed(title="Quote Categories", colour=discord.Colour.blue())
        embed.add_field(name="Category", value=tag_names)

        # Add timestamp to the embed
        embed.timestamp = datetime.utcnow()

        return embed

    def create_author_list_embed(self, authors):
        """ Creates an embed to display the authors available. """
        pass

    def create_quote_detection_embed(self, quote, author, author_picture):
        """ Creates an embed to tell the user if a quote is found. """
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.title = "Quote from *{}*".format(author)
        embed.description = f"```{quote}```"
        embed.set_thumbnail(url=author_picture)
        embed.timestamp = datetime.utcnow()

        return embed

    def create_error_embed(self, message):
        """ Creates an embed to display an error message. """
        embed = discord.Embed(colour=discord.Colour.red())
        embed.title = message
        return embed

    # Event Listeners
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """ Called when a message has a reaction added to it 
        
        When a user reacts to a quote embedded by the bot with the proper reactions,
        it can be sent to him by using DM or it can be saved to their list of personal quotes, 
        it all depends on the reaction used. 
        """

        # Check that the reaction channels is not done on a private channel and the user is not a bot
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
        """ A special method that acts as a cog local pre-invoke hook. """
        await ctx.trigger_typing()
        return await super().cog_before_invoke(ctx)

    async def cog_after_invoke(self, ctx):
        """ A special method that acts as a cog local post-invoke hook. """
        return await super().cog_after_invoke(ctx)

    # Commands
    @commands.command(
        name="quote",
        aliases=["qt", "random"],
        brief="Sends a quote by author and/or tags.",
        help="Sends a quote by author and/or tags.",
    )
    async def quote(self, ctx, tags: str = None, *, author: str = None):
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

        except Exception:
            logger.error("Sorry, could not get quote.")
            embed = self.create_error_embed("Sorry, could not find any quote.")
            await ctx.channel.send(embed=embed)

    @commands.command(
        name="quotes",
        aliases=["qts"],
        brief="Sends a list of quotes by author and/or tags.",
        help="Sends a list of quotes by author and/or tags.",
    )
    async def quotes(
        self, ctx, num_quotes: int = None, tags: str = None, *, author: str = None
    ):
        try:
            # Get list of quotes filtered by tags and author from the api
            query_params = {}

            if num_quotes is not None:
                query_params["tags"] = tags

            if author is not None:
                query_params["author"] = author

            quotes = self.api.get_all_quotes(query_params=query_params).json()

            # Check for any matches
            if len(quotes["records"]) > 0:
                # Create paginated embed and send it over
                # await ctx.channel.send(embed=embed)
                pass

            else:
                raise Exception("No matches found.")

        except Exception:
            logger.error("Could not find any matches")
            embed = self.create_error_embed("Sorry, could not find any matches.")
            await ctx.channel.send(embed=embed)

    @commands.command(
        name="tags",
        aliases=["tgs"],
        brief="Sends a list of all tags available.",
        help="Sends a list of all tags available.",
    )
    async def quote_tags(self, ctx):
        """ Sends a list of all tags available. """
        try:
            # Get list of tags available from the api
            tags = self.api.get_all_tags().json()

            # Create paginated embed and send it over
            # await ctx.channel.send(embed=embed)
            pass

        except Exception:
            logger.error("Could not get available tags")
            embed = self.create_error_embed("Sorry, could not get available tags.")
            await ctx.channel.send(embed=embed)

    @commands.command(
        name="authors",
        aliases=["auts"],
        brief="Sends a list of all the authors available.",
        help="Sends a list of all the authors available.",
    )
    async def quote_authors(self, ctx):
        """ Sends a list of all the authors available. """
        try:
            # Get list of authors available from the api
            authors = self.api.get_all_authors().json()

            # Create paginated embed and send it over
            # await ctx.channel.send(embed=embed)
            pass

        except Exception:
            logger.error("Could not get available authors")
            embed = self.create_error_embed("Sorry, could not get available authors.")
            await ctx.channel.send(embed=embed)

    @commands.command(
        name="detect",
        aliases=["det"],
        brief="Tries to find a match for a quote.",
        help="Tries to find a match for a quote.",
    )
    async def detect_quote(self, ctx, text: str):
        try:
            # Get list of quotes from the api
            quotes = self.api.get_all_quotes(query_params={"query": text}).json()

            # Check for any matches
            if len(quotes["records"]) > 0:
                # Create paginated embed and send it over
                # await ctx.channel.send(embed=embed)
                pass

            else:
                raise Exception("No matches were found.")

        except Exception:
            logger.error("Could not find any matches.")
            embed = self.create_error_embed("Sorry, could not find any matches.")
            await ctx.channel.send(embed=embed)


def setup(bot):
    """ Sets up the quote cog for the bot. """
    logger.info("Loading Quote Cog")
    bot.add_cog(QuoteCog(bot))


def teardown(bot):
    """ Tears down the quote cog for the bot. """
    logger.info("Unloading Quote Cog")
    bot.remove_cog("cogs.quote_cog")
