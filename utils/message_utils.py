"""Safe message handling utilities."""

import asyncio
from typing import Any, Callable, Coroutine, Optional, Union

import discord
from discord.ext import commands

from logger import logger

MessageDestination = Union[
    discord.TextChannel,
    discord.DMChannel,
    discord.Thread,
    discord.User,
    discord.Member,
    commands.Context
]

ErrorHandler = Callable[[Exception], Coroutine[Any, Any, None]]

async def safe_send(
    destination: MessageDestination,
    *,
    content: Optional[str] = None,
    embed: Optional[discord.Embed] = None,
    file: Optional[discord.File] = None,
    files: Optional[list[discord.File]] = None,
    view: Optional[discord.ui.View] = None,
    delete_after: Optional[float] = None,
    error_handler: Optional[ErrorHandler] = None,
    **kwargs
) -> Optional[discord.Message]:
    """Send a message safely with error handling."""
    try:
        return await destination.send(
            content=content,
            embed=embed,
            file=file,
            files=files,
            view=view,
            delete_after=delete_after,
            **kwargs
        )
    except discord.Forbidden:
        await _handle_forbidden_error(destination, error_handler)
    except discord.HTTPException as e:
        await _handle_http_error(e, error_handler)
    except Exception as e:
        logger.error(f"Unexpected error sending message: {e}")
        if error_handler:
            await error_handler(e)
    
    return None

async def safe_reply(
    message: discord.Message,
    *,
    content: Optional[str] = None,
    embed: Optional[discord.Embed] = None,
    file: Optional[discord.File] = None,
    files: Optional[list[discord.File]] = None,
    view: Optional[discord.ui.View] = None,
    delete_after: Optional[float] = None,
    error_handler: Optional[ErrorHandler] = None,
    mention_author: bool = True,
    **kwargs
) -> Optional[discord.Message]:
    """Reply to a message safely with error handling."""
    try:
        return await message.reply(
            content=content,
            embed=embed,
            file=file,
            files=files,
            view=view,
            delete_after=delete_after,
            mention_author=mention_author,
            **kwargs
        )
    except discord.Forbidden:
        await _handle_forbidden_error(message.channel, error_handler)
    except discord.HTTPException as e:
        await _handle_http_error(e, error_handler)
    except Exception as e:
        logger.error(f"Unexpected error replying to message: {e}")
        if error_handler:
            await error_handler(e)
    
    return None

async def _handle_forbidden_error(
    destination: MessageDestination,
    error_handler: Optional[ErrorHandler]
) -> None:
    """Handle forbidden errors by notifying server owner."""
    if error_handler:
        await error_handler(discord.Forbidden(discord.HTTPException(), ""))
        return
    
    # Try to notify server owner if in a guild
    if hasattr(destination, 'guild') and destination.guild:
        guild = destination.guild
        if guild.owner:
            try:
                await guild.owner.send(
                    f"⚠️ I don't have permission to send messages in "
                    f"**{guild.name}** → #{destination.name}"
                )
            except discord.Forbidden:
                logger.warning(f"Cannot DM guild owner for {guild.name}")

async def _handle_http_error(
    error: discord.HTTPException,
    error_handler: Optional[ErrorHandler]
) -> None:
    """Handle HTTP errors."""
    logger.error(f"HTTP error: {error}")
    if error_handler:
        await error_handler(error)

# Backward compatibility
send = safe_send
reply = safe_reply
