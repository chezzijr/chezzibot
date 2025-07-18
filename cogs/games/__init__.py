"""Enhanced Games cog with proper error handling and modern Discord.py 2.x features."""

from __future__ import annotations
from typing import Optional

import discord
from discord.ext import commands

from bot import ChezziBot
from .tictactoe import TicTacToe
from .tictactoe5 import TicTacToe5
from .sokoban import Sokoban
from .rps import RPS
from utils import safe_send
from utils import TimeoutView
from logger import logger

class Games(commands.Cog, name="Games"):
    """Interactive games that you can play with other members or the bot."""

    def __init__(self, bot: ChezziBot) -> None:
        self.bot = bot
        self.visible = True

    @commands.command(name="sokoban", help="Play the classic Sokoban puzzle game")
    async def sokoban(self, ctx: commands.Context):
        """
        A puzzle video game where you push boxes to storage locations.
        Navigate with the arrow buttons and try to complete all levels!
        
        **Usage:** `{prefix}sokoban`
        """
        try:
            view = Sokoban(ctx.author)
            embed = discord.Embed(
                title="🎮 Sokoban",
                description="Use the arrow buttons to move and push boxes to the red targets!",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Controls",
                value="🔄 Restart • ⛔ Stop • ⏩ Next Level",
                inline=False
            )
            embed.add_field(
                name="Board",
                value=f"```\n{view.render_board()}\n```",
                inline=False
            )
            
            message = await safe_send(ctx, embed=embed, view=view)
            await view.wait()
            
            # Handle timeout
            if view.is_finished() and hasattr(view, 'result') and view.result.value == 0:
                timeout_view = TimeoutView()
                await message.edit(embed=embed, view=timeout_view)
                
        except Exception as e:
            logger.error(f"Error in sokoban command: {e}")
            await safe_send(ctx, content="❌ An error occurred while starting the game.")

    @commands.command(
        name="tictactoe",
        aliases=["tic", "tac", "toe"],
        help="Play Tic-Tac-Toe against another player"
    )
    async def tic_tac_toe(self, ctx: commands.Context, opponent: discord.Member):
        """
        Play the classic 3x3 Tic-Tac-Toe game against another player.
        
        **Parameters:**
        - `opponent`: The member you want to play against
        
        **Usage:** `{prefix}tictactoe @user`
        """
        if opponent == ctx.author:
            await safe_send(ctx, content="❌ You can't play against yourself!")
            return
            
        if opponent.bot and opponent != self.bot.user:
            await safe_send(ctx, content="❌ You can only play against me or other users!")
            return

        embed = discord.Embed(
            title="🎮 Tic-Tac-Toe",
            description=f"**{ctx.author.display_name}** (❌) vs **{opponent.display_name}** (⭕)",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Current Turn",
            value=f"It's **{opponent.display_name}**'s turn!",
            inline=False
        )
        
        view = TicTacToe(ctx.author, opponent)
        await safe_send(ctx, embed=embed, view=view)

    @commands.command(
        name="tictactoe5",
        aliases=["tic5", "tac5", "toe5"],
        help="Play 5x5 Tic-Tac-Toe against another player"
    )
    async def tic_tac_toe_5(self, ctx: commands.Context, opponent: discord.Member):
        """
        Play 5x5 Tic-Tac-Toe where you need 4 in a row to win.
        
        **Parameters:**
        - `opponent`: The member you want to play against
        
        **Usage:** `{prefix}tictactoe5 @user`
        """
        if opponent == ctx.author:
            await safe_send(ctx, content="❌ You can't play against yourself!")
            return
            
        if opponent.bot and opponent != self.bot.user:
            await safe_send(ctx, content="❌ You can only play against me or other users!")
            return

        embed = discord.Embed(
            title="🎮 Tic-Tac-Toe 5x5",
            description=f"**{ctx.author.display_name}** (❌) vs **{opponent.display_name}** (⭕)",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Rules",
            value="Get 4 in a row to win!",
            inline=False
        )
        embed.add_field(
            name="Current Turn",
            value=f"It's **{opponent.display_name}**'s turn!",
            inline=False
        )
        
        view = TicTacToe5(ctx.author, opponent)
        await safe_send(ctx, embed=embed, view=view)

    @commands.command(
        name="rockpaperscissors",
        aliases=["rps", "rock", "paper", "scissors"],
        help="Play Rock-Paper-Scissors"
    )
    async def rps(self, ctx: commands.Context, opponent: Optional[discord.Member] = None):
        """
        Play Rock-Paper-Scissors against another player or the bot.
        
        **Parameters:**
        - `opponent`: (Optional) The member you want to play against. If not provided, you'll play against the bot.
        
        **Usage:** 
        - `{prefix}rps` (play against bot)
        - `{prefix}rps @user` (play against user)
        """
        if opponent is None:
            opponent = self.bot.user
            
        if opponent == ctx.author:
            await safe_send(ctx, content="❌ You can't play against yourself!")
            return

        embed = discord.Embed(
            title="🎮 Rock Paper Scissors",
            description=f"**{ctx.author.display_name}** vs **{opponent.display_name}**",
            color=discord.Color.orange()
        )
        embed.add_field(
            name="How to Play",
            value="Click one of the buttons below to make your choice!",
            inline=False
        )
        
        view = RPS(ctx, ctx.author, opponent if opponent != self.bot.user else None)
        await safe_send(ctx, embed=embed, view=view)

async def setup(bot: ChezziBot):
    """Set up the Games cog."""
    await bot.add_cog(Games(bot))
