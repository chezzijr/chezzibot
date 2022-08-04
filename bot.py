import discord
from discord.ext import commands
from log import logger
from aiohttp import ClientSession

COGS = (
    "audio",
    "events",
    "games",
    "help",
    "media",
    "utilities",
)


class ChezziBot(commands.AutoShardedBot):
    def __init__(
            self,
            *,
            http_session: ClientSession,
            **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.http_session = http_session

    async def setup_hook(self) -> None:
        for cog in COGS:
            await self.load_extension(f"cogs.{cog}")

    async def process_commands(self, message: discord.Message, /) -> None:
        if message.author.bot:
            return

        ctx = await self.get_context(message)

        if ctx.command and \
                ((hasattr(ctx.command, "cog") and
                 hasattr(ctx.command.cog, "visible") and
                 ctx.command.cog.visible) or
                 ctx.command.name == "help"):
            await self.invoke(ctx)

    async def on_ready(self):
        activity = discord.Game("t.help help")
        await self.change_presence(status=discord.Status.idle, activity=activity)
