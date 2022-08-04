import discord


async def get_attachment(message: discord.Message, content_type: str | list[str]) -> discord.Attachment | None:
    """
    Get the first attachment from the message
    Priority: original message > reference message

    Parameters
    -------
    message: discord.Message
        The original message
    content_type: str
        The type of attachment

    Return
    -------
    First attachment with `content_type`
    """
    if isinstance(content_type, str):
        content_type = [content_type]

    for attachment in message.attachments:
        if attachment.content_type in content_type:
            return attachment

    if (ref := message.reference) is not None:
        msg = await message.channel.fetch_message(ref.message_id)
        for attachment in msg.attachments:
            if attachment.content_type in content_type:
                return attachment

    return None


async def get_attachments(message: discord.Message, content_type: str | list[str]) -> list[discord.Attachment]:
    """
    Get all attachments from the message, including the reference message

    Parameters
    -------
    message: discord.Message
        The original message
    content_type: str
        The type of attachment

    Return
    -------
    All attachments with `content_type`
    """
    if isinstance(content_type, str):
        content_type = [content_type]

    original_attachments = filter(
        lambda a: a.content_type in content_type, message.attachments)

    if (ref := message.reference) is not None:
        msg = await message.channel.fetch_message(ref.message_id)
        ref_attachments = filter(
            lambda a: a.content_type in content_type, msg.attachments)

        return list(original_attachments) + list(ref_attachments)

    return list(original_attachments)
