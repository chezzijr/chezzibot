import discord
from typing import Any, Callable, Coroutine, Optional
from discord.ext import commands
from log import logger

# Send handler section
Sendable = discord.abc.Messageable
SendErrorHandler = Callable[[
    Sendable, discord.HTTPException | discord.Forbidden | ValueError | TypeError], Coroutine[Any, Any, None]]


async def send(
        dest: Sendable,
        *,
        invoker: Optional[discord.Member | discord.User] = None,
        handler: Optional[SendErrorHandler] = None,
        allow_recursion: bool = True,
        **kwargs: dict[str, Any]) -> discord.Message | None:

    msg = None
    try:
        msg = await dest.send(**kwargs)
    # Try notify the owner as there might be lack of permissions (only in server's channel)
    except discord.Forbidden as e:
        if handler:
            await handler(dest, e)
        else:
            guild = None
            d = await dest._get_channel()

            if isinstance(dest, (discord.TextChannel, discord.Thread, commands.Context)):
                guild = dest.guild

            if guild and allow_recursion:  # Error occur in server -> no permissions, otherwise there is no fix
                # Try sending error to system channel
                syschannel = guild.system_channel
                if syschannel:
                    # Turn off allow_recursion to prevent inf recursion
                    await send(
                        syschannel,
                        handler=handler,
                        allow_recursion=False,
                        content="{} I do not have the permission to send messages to {}"
                        .format(
                            invoker.mention if invoker else "",
                            syschannel.mention
                        )
                    )

                # Try sending error to server owner
                else:
                    owner = guild.owner
                    if owner:
                        await send(
                            owner,
                            handler=handler,
                            allow_recursion=False,
                            content=(
                                f"I do not have the permission to send messages to `{d.name}` "
                                f"which belongs to your server `{guild.name}`"
                            )
                        )

        logger.error(e)

    # Can only log out error due to errors in codebase or network
    except (discord.HTTPException, ValueError, TypeError) as e:
        if handler:
            await handler(dest, e)

        logger.error(e)

    # return message if successfully sent, else None
    finally:
        return msg

# Reply handler section
ReplyHandler = SendErrorHandler = Callable[[
    discord.Message, discord.HTTPException | discord.Forbidden | ValueError | TypeError], Coroutine[Any, Any, None]]


async def reply(
        reply_to: discord.Message,
        *,
        handler: Optional[ReplyHandler] = None,
        allow_recursion: bool = True,
        **kwargs: dict[str, Any]) -> discord.Message | None:

    msg = None
    try:
        msg = await reply_to.reply(**kwargs)

    # Try notify the owner as there might be lack of permissions (only in server's channel)
    except discord.Forbidden as e:
        if handler:
            await handler(reply_to, e)
        else:
            guild = reply_to.guild
            channel = reply_to.channel

            if guild and allow_recursion:  # Error occur in server -> no permissions, otherwise there is no fix
                # Try sending error to system channel
                syschannel = guild.system_channel
                if syschannel:
                    # Turn off allow_recursion to prevent inf recursion
                    await send(
                        syschannel,
                        handler=handler,
                        allow_recursion=False,
                        content="{} I do not have the permission to send messages to {}"
                        .format(
                            reply_to.author.mention,
                            syschannel.mention
                        )
                    )

                # Try sending error to server owner
                else:
                    owner = guild.owner
                    if owner:
                        await send(
                            owner,
                            handler=handler,
                            allow_recursion=False,
                            content=(
                                f"I do not have the permission to reply messages to `{reply_to.author}`'s message "
                                f"which belongs to your server `{guild.name}` and in channel `{channel}`"
                            )
                        )

        logger.error(e)

    # Can only log out error due to errors in codebase or network
    except (discord.HTTPException, ValueError, TypeError) as e:
        if handler:
            await handler(reply_to, e)

        logger.error(e)

    # return message if successfully sent, else None
    finally:
        return msg
