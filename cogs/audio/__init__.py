import discord
from log import logger
from io import BytesIO
from discord.ext import commands
from bot import ChezziBot
from utils import reply, FFmpegPCMAudio, Timeout
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

    @commands.command(name="fifteenaitts", aliases=["fifteenai", "15aitts", "15ai", "15tts"])
    async def tts(self, ctx: commands.Context, *, text: str):
        """
        Convert a text to speech based on some characters
        Credit to 15.ai for tts
        English only

        Parameters
        -------
        text: str
            The text that bot will speak (5 - 200 characters)

        Aliases
        -------
        fifteenaitts, fifteenai, 15aitts, 15ai, 15tts

        Examples
        -------
        t.15ai me when your mom
        """
        if ctx.voice_client is None:
            return await reply(ctx.message, content="Not connected to a voice channel")

        view = FifteenAIView()
        msg = await reply(ctx.message, view=view)

        await view.wait()

        if msg:
            if view.character:
                with BytesIO() as fileobj:
                    resp = await save_to_bytesio(self.bot.http_session, view.character, text, fileobj)
                    if resp["status"] == "OK":
                        src = discord.PCMVolumeTransformer(
                            FFmpegPCMAudio(fileobj.read(), pipe=True))
                        ctx.voice_client.play(source=src, after=lambda e: logger.error(
                            f'Player error: {e}') if e else None)
                    else:
                        await msg.edit(content=resp["status"])
            else:
                await msg.edit(view=Timeout())

    @tts.before_invoke
    async def ensure_voice(self, ctx: commands.Context):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError(
                    "Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


async def setup(bot):
    await bot.add_cog(Audio(bot))
