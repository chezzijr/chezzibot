from discord.ext import commands
from bot import ChezziBot


class Ulitities(commands.Cog):
    """
    Containing some useful commands
    """

    def __init__(self, bot: ChezziBot):
        self.bot = bot
        self.visible = True


async def setup(bot):
    await bot.add_cog(Ulitities(bot))
