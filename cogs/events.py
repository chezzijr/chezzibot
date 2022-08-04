import discord
import os
from typing import TypeVar
from discord.ext import commands
from log import logger
from bot import ChezziBot
from utils import send


class Event(commands.Cog):
    def __init__(self, bot: ChezziBot) -> None:
        self.bot = bot
        self.visible = False

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(
            f"Logged in as {self.bot.user}. Watching over {len(self.bot.guilds)} servers")

    @commands.Cog.listener()
    async def on_guild_join(self, _: discord.Guild):
        logger.info(
            f"Added to a server. Currently watching over {len(self.bot.guilds)} servers")

    @commands.Cog.listener()
    async def on_guild_remove(self, _: discord.Guild):
        logger.info(
            f"Removed from a server. Currently watching over {len(self.bot.guilds)} servers")

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        ...


async def setup(bot):
    await bot.add_cog(Event(bot))
