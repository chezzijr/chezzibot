"""Event handling cog for ChezziBot."""

import discord
from discord.ext import commands

from logger import logger
from bot import ChezziBot

class EventsCog(commands.Cog, name="Events"):
    """Handles bot events and logging."""
    
    def __init__(self, bot: ChezziBot):
        self.bot = bot
        self.visible = False
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Event fired when bot is ready."""
        logger.info(f"Bot is ready! Serving {len(self.bot.guilds)} guilds.")
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Event fired when bot joins a guild."""
        logger.info(f"Joined guild: {guild.name} (ID: {guild.id}, Members: {guild.member_count})")
        
        # Try to send a welcome message
        if guild.system_channel:
            embed = discord.Embed(
                title="👋 Hello!",
                description=(
                    f"Thanks for adding me to **{guild.name}**!\n\n"
                    f"• Use `{self.bot.command_prefix}help` to see my commands\n"
                    f"• I'm here to help with games, media, and utilities\n"
                    f"• For support, contact my owner"
                ),
                color=discord.Color.green()
            )
            try:
                await guild.system_channel.send(embed=embed)
            except discord.Forbidden:
                logger.warning(f"Cannot send welcome message in {guild.name}")
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        """Event fired when bot leaves a guild."""
        logger.info(f"Left guild: {guild.name} (ID: {guild.id})")
    
    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context):
        """Event fired when a command completes successfully."""
        logger.info(
            f"Command '{ctx.command.name}' used by {ctx.author} "
            f"in {ctx.guild.name if ctx.guild else 'DM'}"
        )
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """Handle command errors that weren't handled by the global handler."""
        # Let the global handler deal with it
        pass

async def setup(bot: ChezziBot):
    """Set up the events cog."""
    await bot.add_cog(EventsCog(bot))
