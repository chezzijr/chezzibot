import discord
from logger import logger
from io import BytesIO
from discord.ext import commands
from bot import ChezziBot
from utils import reply, FFmpegPCMAudio, TimeoutView
from .fifteenai import FifteenAIView, save_to_bytesio


class Audio(commands.Cog):
    """
    Containing commands relating to audios
    Usable only when bot is in voice channel
    """

    def __init__(self, bot: ChezziBot) -> None:
        self.bot = bot
        self.visible = True

    @commands.command()
    async def join(self, ctx: commands.Context, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to()

        await channel.connect()

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()
