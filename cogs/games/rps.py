"""Enhanced Rock Paper Scissors game with better UX and error handling."""

import discord
import random
from typing import Optional
from logger import logger

def compare_choices(first: int, second: int) -> Optional[bool]:
    """
    Compare two choices to determine winner.
    
    Args:
        first: First player's choice (1=rock, 2=paper, 3=scissors)
        second: Second player's choice (1=rock, 2=paper, 3=scissors)
        
    Returns:
        True if second beats first, False if first beats second, None if tie
    """
    if first == second:
        return None
    
    winning_combinations = {
        (1, 2),  # Paper beats Rock
        (2, 3),  # Scissors beats Paper
        (3, 1),  # Rock beats Scissors
    }
    
    return (first, second) in winning_combinations

def get_choice_name(choice: int) -> str:
    """Get the display name for a choice."""
    return {1: "🪨 Rock", 2: "📄 Paper", 3: "✂️ Scissors"}[choice]

def get_choice_emoji(choice: int) -> str:
    """Get the emoji for a choice."""
    return {1: "🪨", 2: "📄", 3: "✂️"}[choice]

class RPS(discord.ui.View):
    """Rock Paper Scissors game view."""
    
    def __init__(self, ctx, first: discord.Member, second: Optional[discord.Member] = None):
        super().__init__(timeout=180.0)
        
        self.ctx = ctx
        self.players = [first, ctx.bot.user if second is None else second]
        self.choices = [None, random.randint(1, 3) if second is None else None]
        self.is_bot_game = second is None
        
        # Update button labels with emojis
        self.children[0].emoji = "🪨"
        self.children[1].emoji = "📄"
        self.children[2].emoji = "✂️"

    def get_player_index(self, user: discord.User) -> int:
        """Get the index of a player."""
        try:
            return self.players.index(user)
        except ValueError:
            return -1

    async def end_game(self, interaction: discord.Interaction):
        """End the game and show results."""
        self.stop()
        for item in self.children:
            item.disabled = True

        result = compare_choices(self.choices[0], self.choices[1])
        
        embed = discord.Embed(
            title="🎮 Rock Paper Scissors - Results",
            color=discord.Color.green() if result is None else discord.Color.blue()
        )
        
        # Show choices
        embed.add_field(
            name=f"{self.players[0].display_name}'s Choice",
            value=get_choice_name(self.choices[0]),
            inline=True
        )
        embed.add_field(
            name=f"{self.players[1].display_name}'s Choice",
            value=get_choice_name(self.choices[1]),
            inline=True
        )
        
        # Show result
        if result is None:
            embed.add_field(
                name="Result",
                value="🤝 It's a tie!",
                inline=False
            )
        elif result:
            winner = self.players[1]
            embed.add_field(
                name="Result",
                value=f"🎉 **{winner.display_name}** wins!",
                inline=False
            )
        else:
            winner = self.players[0]
            embed.add_field(
                name="Result",
                value=f"🎉 **{winner.display_name}** wins!",
                inline=False
            )

        await interaction.response.edit_message(embed=embed, view=self)

    async def make_choice(self, interaction: discord.Interaction, choice: int):
        """Handle a player making a choice."""
        player_index = self.get_player_index(interaction.user)
        if player_index == -1:
            await interaction.response.send_message(
                "❌ You're not part of this game!", ephemeral=True
            )
            return
        
        self.choices[player_index] = choice
        
        if all(c is not None for c in self.choices):
            await self.end_game(interaction)
        else:
            # Wait for other player
            waiting_for = self.players[1 - player_index]
            embed = discord.Embed(
                title="🎮 Rock Paper Scissors",
                description=f"**{self.players[0].display_name}** vs **{self.players[1].display_name}**",
                color=discord.Color.orange()
            )
            embed.add_field(
                name="Status",
                value=f"Waiting for **{waiting_for.display_name}** to make their choice...",
                inline=False
            )
            
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Rock", style=discord.ButtonStyle.primary)
    async def rock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle rock choice."""
        await self.make_choice(interaction, 1)

    @discord.ui.button(label="Paper", style=discord.ButtonStyle.secondary)
    async def paper_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle paper choice."""
        await self.make_choice(interaction, 2)

    @discord.ui.button(label="Scissors", style=discord.ButtonStyle.success)
    async def scissors_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle scissors choice."""
        await self.make_choice(interaction, 3)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if the user can interact with this view."""
        if interaction.user not in self.players:
            await interaction.response.send_message(
                "❌ You cannot play in this game!", ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        """Handle view timeout."""
        for item in self.children:
            item.disabled = True
        
        embed = discord.Embed(
            title="🎮 Rock Paper Scissors - Timeout",
            description="The game has timed out.",
            color=discord.Color.red()
        )
        
        try:
            # Try to edit the message if possible
            await self.ctx.edit_last_response(embed=embed, view=self)
        except:
            # If that fails, send a new message
            await self.ctx.send(embed=embed, view=self)
