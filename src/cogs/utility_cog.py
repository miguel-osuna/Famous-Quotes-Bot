"""Discord bot Utility cog."""

import asyncio
import itertools

import discord
from discord.ext import commands

from util import generate_logger, Pages
from config import SUPPORT_SERVER_INVITE_URL

logger = generate_logger(__name__)


class HelpPaginator(Pages):
    """Paginator for Custom Help Command."""

    def __init__(self, help_command, ctx, entries, *, per_page=4):
        super().__init__(ctx, entries=entries, per_page=per_page)

        # Add question mark emoji for help paginator
        self.reaction_emojis.append(
            ("\N{WHITE QUESTION MARK ORNAMENT}", self.show_bot_help)
        )
        self.total = len(entries)
        self.help_command = help_command
        self.prefix = help_command.clean_prefix
        self.is_bot = False

    def get_bot_page(self, page):
        """Gets a list of page commands."""
        cog, description, commands = self.entries[page - 1]
        self.title = f"{cog} Commands"
        self.description = description
        return commands

    def prepare_embed(self, entries, page, *, first=False):
        """Prepares the pagination page message."""
        self.embed.clear_fields()
        self.embed.title = self.title
        self.embed.description = self.description

        # Add Page location header
        if self.maximum_pages:
            self.embed.set_author(
                name=f"Page {page}/{self.maximum_pages} ({self.total} commands)"
            )

        # Check if the client is a bot to display the support server
        server_invite_url = SUPPORT_SERVER_INVITE_URL
        if self.is_bot:
            value = f"For more help, join the official bot support server: {server_invite_url}"
            self.embed.add_field(name="Support", value=value, inline=False)

        # Add footer to show how to use the help command
        self.embed.set_footer(
            text=f'Use "{self.prefix}help command" for more info on a command.'
        )

        for entry in entries:
            signature = f"{entry.qualified_name} {entry.signature}"
            self.embed.add_field(
                name=signature, value=entry.short_doc or "No help given", inline=False
            )

    async def show_help(self):
        """Shows this message."""

        self.embed.title = "Paginator help"
        self.embed.description = "Hi! Welcome to the bot help page."
        self.embed.clear_fields()

        messages = [f"{emoji} {func.__doc__}" for emoji, func in self.reaction_emojis]
        self.embed.add_field(
            name="What are these reactions for?",
            value="\n".join(messages),
            inline=False,
        )

        self.embed.set_footer(
            text=f"We were on page {self.current_page} before this message."
        )
        await self.message.edit(embed=self.embed)

        # Go back to previous page after 30 seconds
        async def go_back_to_current_page():
            await asyncio.sleep(30.0)
            await self.show_current_page()

        self.bot.loop.create_task(go_back_to_current_page())

    async def show_bot_help(self):
        """Shows how to use the bot."""

        self.embed.title = "Using the bot"
        self.embed.description = "Hi! Welcome to the bot help page."
        self.embed.clear_fields()

        self.embed.add_field(
            name="How do I use this bot?",
            value="Reading the bot signature is pretty simple.",
        )

        entries = (
            ("<argument>", "This means the argument is __**required**__."),
            ("[argument]", "This means the argument is __**optional**__."),
            ("[A|B]", "This means that it can be __**either A or B**__."),
            (
                "[argument...]",
                "This means you can have multiple arguments.\n"
                "Now that you know the basics, it should be noted that...\n"
                "__**You do not type in the brackets!**__",
            ),
        )

        for name, value in entries:
            self.embed.add_field(name=name, value=value, inline=False)

        self.embed.set_footer(
            text=f"We were on page {self.current_page} before this message."
        )
        await self.message.edit(embed=self.embed)

        # Go back to previous page after 30 seconds
        async def go_back_to_current_page():
            await asyncio.sleep(30.0)
            await self.show_current_page()

        self.bot.loop.create_task(go_back_to_current_page())


class PaginatedHelpCommand(commands.HelpCommand):
    """Class for a bot paginated help command."""

    def __init__(self):
        super().__init__(
            command_attrs={
                "cooldown": commands.Cooldown(1, 3.0, commands.BucketType.member),
                "help": "Shows help about the bot, a command, or a category",
            }
        )

    async def on_help_command_error(self, ctx, error):
        """Callback to run on help command error."""
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(str(error.original))

    def get_command_signature(self, command):
        """Retrievers the signature portion of a command."""
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = "|".join(command.aliases)
            fmt = f"[{command.name}|{aliases}]"
            if parent:
                fmt = f"{parent} {fmt}"
            alias = fmt
        else:
            alias = command.name if not parent else f"{parent} {command.name}"
        return f"{alias} {command.signature}"

    async def send_bot_help(self, mapping):
        """Handles the implementation of the bot command page in the help command.

        This function is called when the help command is called with no arguments.
        """

        def key(cog):
            return cog.cog_name or "\u200bNo Category"

        bot = self.context.bot
        entries = await self.filter_commands(bot.commands, sort=True, key=key)
        nested_pages = []
        per_page = 9
        total = 0

        for cog, commands in itertools.groupby(entries, key=key):
            commands = sorted(commands, key=lambda c: c.name)
            if len(commands) == 0:
                continue

            total += len(commands)
            actual_cog = bot.get_cog(cog)

            # Get the description if it exists (and the cog is valid) or return Empty embed.
            description = actual_cog.description if actual_cog else discord.Embed.Empty

            # Generate the pages for the cog commands
            nested_pages.extend(
                (cog, description, commands[i : i + per_page])
                for i in range(0, len(commands), per_page)
            )

        # A value of 1 forces the pagination session
        pages = HelpPaginator(self, self.context, nested_pages, per_page=1)

        # Swap the get_page implementation to work with our nested pages.
        pages.get_page = pages.get_bot_page
        pages.is_bot = True
        pages.total = total
        # await self.context.release()
        await pages.paginate()

    async def send_cog_help(self, cog):
        """Handles the implementation of the cog page in the help command.

        This function is called when the help command is called with a cog as
        the argument
        """
        entries = await self.filter_commands(cog.get_commands(), sort=True)

        # Create a Help Paginator by using the cog command entries
        pages = HelpPaginator(self, self.context, entries)
        pages.title = f"{cog.qualified_name} Commands"
        pages.description = cog.description

        # await self.context.release()
        await pages.paginate()

    def common_command_formatting(self, page_or_embed, command):
        """Creates a command format for a page or embed."""
        page_or_embed.title = self.get_command_signature(command)
        if command.description:
            page_or_embed.description = f"{command.description}\n\n{command.help}"
        else:
            page_or_embed.description = command.help or "No help found..."

    async def send_command_help(self, command):
        """Callback to run on send command help."""

        # No pagination necessary for a single command.
        embed = discord.Embed(colour=discord.Colour.blue())
        self.common_command_formatting(embed, command)
        await self.context.send(embed=embed)

    async def send_group_help(self, group):
        """Callback to run on send group help."""
        subcommands = group.commands
        if len(subcommands) == 0:
            return await self.send_command_help(group)

        entries = await self.filter_commands(subcommands, sort=True)
        pages = HelpPaginator(self, self.context, entries)
        self.common_command_formatting(pages, group)

        # await self.context.release()
        await pages.paginate()


class Utility(commands.Cog):
    """General utility commands."""

    def __init__(self, bot):
        # Switch the bot help command to the PaginatedHelpCommand
        self.bot = bot
        self.old_help_command = bot.help_command
        bot.help_command = PaginatedHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        """Unload a cog from the bot."""
        self.bot.help_command = self.old_help_command

    # Class Methods
    async def cog_before_invoke(self, ctx):
        """A special method that acts as a cog local pre-invoke hook."""
        await ctx.trigger_typing()
        return await super().cog_before_invoke(ctx)

    async def cog_after_invoke(self, ctx):
        """A special method that acts as a cog local post-invoke hook."""
        return await super().cog_after_invoke(ctx)

    # Commands
    @commands.is_owner()
    @commands.command(
        name="load",
        brief="Loads a specified extension/cog",
        help="Loads a specified extension/cog",
        hidden=True,
    )
    async def load_cog(self, ctx, *, cog: str):
        """Command which loads a module."""
        try:
            self.bot.load_extension(f"cogs.{cog}")
        except Exception as exc:  # pylint: disable=broad-except
            await ctx.send(f"**`ERROR`:** {type(exc).__name__} - {exc}")
        else:
            await ctx.send("**`SUCCESS`**")

    @commands.is_owner()
    @commands.command(
        name="unload",
        brief="Unloads a specified extension/cog",
        help="Unloads a specified extension/cog",
        hidden=True,
    )
    async def unload_cog(self, ctx, *, cog: str):
        """Command which unloads a module."""
        try:
            self.bot.unload_extension(f"cogs.{cog}")
        except Exception as exc:  # pylint: disable=broad-except
            await ctx.send(f"**`ERROR`:** {type(exc).__name__} - {exc}")
        else:
            await ctx.send("**`SUCCESS`**")

    @commands.is_owner()
    @commands.command(
        name="reload",
        brief="Reloads a specified extension/cog",
        help="Reloads a specific extension/cog",
        hidden=True,
    )
    async def reload_cog(self, ctx, *, cog: str):
        """Command which reloads a module."""
        try:
            self.bot.reload_extension(f"cogs.{cog}")
        except Exception as exc:  # pylint: disable=broad-except
            await ctx.send(f"**`ERROR`:** {type(exc).__name__} - {exc}")
        else:
            await ctx.send("**`SUCCESS`**")


def setup(bot):
    """Sets up the help cog for the bot."""
    logger.info("Loading Help Cog")
    bot.add_cog(Utility(bot))


def teardown(bot):
    """Tears down the help cog for the bot."""
    logger.info("Unloading Help Cog")
    bot.remove_cog("cogs.help_cog")
