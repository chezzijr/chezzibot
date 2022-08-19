from __future__ import annotations
from typing import Optional
from discord import Member
from discord.ext import commands
from bot import ChezziBot
from .tictactoe import TicTacToe
from .tictactoe5 import TicTacToe5
from .sokoban import Sokoban
from .rps import RPS
from utils import reply
import discord
__all__ = (
    "Games"
    "setup"
)


class Games(commands.Cog):
    """
    Containing all commands relating to games,
    which is playable with other members or bot 
    """

    def __init__(self, bot: ChezziBot) -> None:
        self.bot = bot
        self.visible = True

    @commands.command(
        name="sokoban",
    )
    async def sokoban(self, ctx: commands.Context):
        """
        A puzzle video game genre in which the player pushes crates or boxes around
        in a warehouse, trying to get them to storage locations.

        Parameters
        -------
        None

        Aliases
        -------
        sokoban

        Examples
        -------
        t.sokoban
        `@ChezziBot` sokoban
        """

        view = Sokoban(ctx.author)
        msg = await reply(ctx, content=view.render_board(), view=view)
        await view.wait()

        if view.result.value == 0:
            await msg.edit(
                content=view.render_board(),
                view=view.clear_items().add_item(
                    discord.ui.Button(
                        style=discord.ButtonStyle.gray,
                        label="Timeout",
                        emoji="⚠",
                        disabled=True
                    )
                )
            )

    @ commands.command(
        name="tictactoe",
        aliases=["tic", "tac", "toe"]
    )
    async def tic_tac_toe(self, ctx: commands.Context, opponent: Member):
        """
        A paper-and-pencil game for two players who take turns marking the spaces
        in a 3x3 grid with X or O. The player who succeeds in placing
        three of their marks in a horizontal, vertical, or diagonal row is the winner

        Parameters
        -------
        opponent: Member
            A member that you will play tic tac toe against

        Aliases
        -------
        tictactoe, tic, tac, toe

        Examples
        -------
        t.tictactoe `@ChezziBot`
        `@ChezziBot` tic `@DeezNuts`
        """
        return await reply(
            ctx,
            content=f"It is now `{opponent.display_name}`'s turn",
            view=TicTacToe(ctx.author, opponent
                           ))

    @commands.command(
        name="tictactoe5",
        aliases=["tic5", "tac5", "toe5"]
    )
    async def tic_tac_toe_5(self, ctx: commands.Context, opponent: Member):
        """
        A variant of traditional tic tac toe with 5x5 grid. The who succeeds in placing
        four or more of their marks in a horizontal, vertical, or diagonal row is the winner

        Parameters
        -------
        opponent: Member
            A member that you will play tic tac toe against

        Aliases
        -------
        tictactoe5, tic5, tac5, toe5

        Examples
        -------
        t.tictactoe5 `@ChezziBot`
        `@ChezziBot` tic5 `@DeezNuts`
        """

        return await reply(
            ctx,
            content=f"It is now `{opponent.display_name}`'s turn",
            view=TicTacToe5(ctx.author, opponent
                            ))

    @commands.command(
        name="rockpaperscissors",
        aliases=["rps", "rock", "paper", "scissor"],
    )
    async def rps(self, ctx: commands.Context, opponent: Optional[Member] = None):
        """
        A traditional Rock - Paper - Scissors game

        Parameters
        -------
        opponent: Optional[Member]
            A member that you will play Rock - Paper - Scissors against
            If nothing is provided, you will play againt bot

        Aliases
        -------
        rockpaperscissors, rps, rock, paper, scissors

        Examples
        -------
        t.rps `@ChezziBot`
        `@ChezziBot` rock
        """
        if opponent is None or opponent == ctx.me:
            content = f"`{ctx.author.display_name}` vs `{self.bot.user.display_name}`"
            view = RPS(ctx, ctx.author)
        else:
            content = f"`{ctx.author.display_name}` vs `{opponent.display_name}`"
            view = RPS(ctx, ctx.author, opponent)
        await reply(ctx, content=content, view=view)


async def setup(bot):
    await bot.add_cog(Games(bot))
