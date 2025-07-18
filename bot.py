"""Main bot class for ChezziBot."""

import asyncio
from datetime import timedelta
import traceback
from typing import Optional, Union

import discord
from discord.ext import commands
from aiohttp import ClientSession

from logger import logger
import config

class ChezziBot(commands.Bot):
    """Enhanced Discord bot with modern features."""
    
    def __init__(self, http_session: ClientSession, **kwargs):
        super().__init__(
            command_prefix=self._get_prefix,
            intents=config.INTENTS,
            help_command=None,
            case_insensitive=True,
            strip_after_prefix=True,
            owner_id=config.OWNER_ID,
            **kwargs
        )
        
        self.http_session = http_session
        self.start_time = discord.utils.utcnow()
        
        # Extensions to load
        self.extensions_to_load = [
            "cogs.events",
            "cogs.help",
            "cogs.games",
            "cogs.media",
            "cogs.utilities",
            "cogs.audio",
        ]
    
    async def _get_prefix(self, bot: "ChezziBot", message: discord.Message) -> list[str]:
        """Get command prefixes for the bot."""
        prefixes = [config.DEFAULT_PREFIX]
        
        # Allow bot mentions as prefix
        if message.guild:
            prefixes.append(f"<@{self.user.id}> ")
            prefixes.append(f"<@!{self.user.id}> ")
        
        return prefixes
    
    async def setup_hook(self) -> None:
        """Set up the bot before it starts."""
        logger.info("Setting up bot...")
        
        # Load extensions
        for extension in self.extensions_to_load:
            try:
                await self.load_extension(extension)
                logger.info(f"Loaded extension: {extension}")
            except Exception as e:
                logger.error(f"Failed to load extension {extension}: {e}")
                traceback.print_exc()
        
        # Sync application commands (if any)
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} application commands")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self) -> None:
        """Event fired when the bot is ready."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        
        # Set bot presence
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | {config.DEFAULT_PREFIX}help"
        )
        await self.change_presence(
            status=discord.Status.online,
            activity=activity
        )
    
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Event fired when bot joins a guild."""
        logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")
        await self._update_presence()
    
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Event fired when bot leaves a guild."""
        logger.info(f"Left guild: {guild.name} (ID: {guild.id})")
        await self._update_presence()
    
    async def _update_presence(self) -> None:
        """Update bot presence with current guild count."""
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | {config.DEFAULT_PREFIX}help"
        )
        await self.change_presence(activity=activity)
    
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Global error handler for commands."""
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
            return
        
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument provided: {error}")
            return
        
        if isinstance(error, commands.MissingPermissions):
            perms = ", ".join(error.missing_permissions)
            await ctx.send(f"❌ You need the following permissions: {perms}")
            return
        
        if isinstance(error, commands.BotMissingPermissions):
            perms = ", ".join(error.missing_permissions)
            await ctx.send(f"❌ I need the following permissions: {perms}")
            return
        
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Command is on cooldown. Try again in {error.retry_after:.1f} seconds.")
            return
        
        # Log unexpected errors
        logger.error(f"Unexpected error in command {ctx.command}: {error}")
        traceback.print_exc()
        
        await ctx.send("❌ An unexpected error occurred. Please try again later.")
    
    async def process_commands(self, message: discord.Message) -> None:
        """Process commands with enhanced filtering."""
        if message.author.bot:
            return
        
        # Get context
        ctx = await self.get_context(message)
        
        if not ctx.command:
            return
        
        # Check if command is from a visible cog
        if (hasattr(ctx.command, 'cog') and 
            hasattr(ctx.command.cog, 'visible') and 
            not ctx.command.cog.visible and 
            ctx.command.name != 'help'):
            return
        
        await self.invoke(ctx)
    
    async def close(self) -> None:
        """Clean up resources before shutting down."""
        logger.info("Shutting down bot...")
        
        if hasattr(self, 'http_session') and not self.http_session.closed:
            await self.http_session.close()
        
        await super().close()
    
    @property
    def uptime(self) -> timedelta:
        """Get bot uptime."""
        return discord.utils.utcnow() - self.start_time
