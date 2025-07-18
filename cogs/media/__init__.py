"""Enhanced Media cog with better error handling and modern features."""

from __future__ import annotations
from typing import Optional

import discord
from discord.ext import commands
from PIL import Image as PILImage, ImageSequence
from io import BytesIO

from bot import ChezziBot
from utils.message_utils import safe_send
from utils.get_attachment import get_attachment
from .topbottom import handle_image, handle_gif, TopBottomFlags
from .caption import caption_image, caption_gif
from logger import logger
import config

class Media(commands.Cog, name="Media"):
    """Image and GIF processing commands for memes and media manipulation."""

    def __init__(self, bot: ChezziBot) -> None:
        self.bot = bot
        self.visible = True

    @commands.command(
        name="topbottom",
        aliases=["tb", "meme"],
        help="Add top and bottom text to images"
    )
    async def write_top_bottom_text(
        self,
        ctx: commands.Context,
        *,
        flags: TopBottomFlags
    ):
        """
        Add top and bottom text to images and GIFs using Impact font.
        
        **Parameters:**
        - `top`: (Optional) The text to add at the top
        - `bottom`: (Optional) The text to add at the bottom
        
        **Supported formats:** JPG, JPEG, PNG, GIF
        
        **Usage:** 
        - `{prefix}topbottom top: "When you" bottom: "Bottom text"`
        - `{prefix}tb top: "Top text"`
        
        **Note:** Attach an image or reply to a message with an image.
        """
        if not flags.top and not flags.bottom:
            embed = discord.Embed(
                title="❌ Missing Text",
                description="You must specify either `top:` or `bottom:` text (or both).",
                color=discord.Color.red()
            )
            embed.add_field(
                name="Example",
                value=f"`{ctx.prefix}topbottom top: \"When you\" bottom: \"Bottom text\"`",
                inline=False
            )
            await safe_send(ctx, embed=embed)
            return

        # Show processing message
        processing_embed = discord.Embed(
            title="🔄 Processing...",
            description="Processing your image, please wait...",
            color=discord.Color.blue()
        )
        processing_msg = await safe_send(ctx, embed=processing_embed)

        try:
            # Try to get image attachment
            img_attachment = await get_attachment(
                ctx.message, 
                ["image/jpeg", "image/jpg", "image/png"]
            )
            
            if img_attachment:
                async with self.bot.http_session.get(img_attachment.url) as response:
                    if response.status == 200:
                        img_bytes = BytesIO(await response.read())
                        img = PILImage.open(img_bytes)
                        
                        # Delete processing message
                        if processing_msg:
                            await processing_msg.delete()
                        
                        await handle_image(
                            ctx, img, img_attachment.width, 
                            img_attachment.height, flags.top, flags.bottom
                        )
                        return
            
            # Try to get GIF attachment
            gif_attachment = await get_attachment(ctx.message, "image/gif")
            
            if gif_attachment:
                async with self.bot.http_session.get(gif_attachment.url) as response:
                    if response.status == 200:
                        gif_bytes = BytesIO(await response.read())
                        gif_img = PILImage.open(gif_bytes)
                        
                        # Delete processing message
                        if processing_msg:
                            await processing_msg.delete()
                        
                        await handle_gif(
                            ctx, ImageSequence.Iterator(gif_img),
                            gif_attachment.width, gif_attachment.height,
                            flags.top, flags.bottom
                        )
                        return
            
            # No attachment found
            error_embed = discord.Embed(
                title="❌ No Image Found",
                description="Please attach an image or reply to a message with an image.",
                color=discord.Color.red()
            )
            error_embed.add_field(
                name="Supported Formats",
                value="JPG, JPEG, PNG, GIF",
                inline=False
            )
            
            if processing_msg:
                await processing_msg.edit(embed=error_embed)
            else:
                await safe_send(ctx, embed=error_embed)
                
        except Exception as e:
            logger.error(f"Error in topbottom command: {e}")
            error_embed = discord.Embed(
                title="❌ Processing Error",
                description="An error occurred while processing your image.",
                color=discord.Color.red()
            )
            
            if processing_msg:
                await processing_msg.edit(embed=error_embed)
            else:
                await safe_send(ctx, embed=error_embed)

    @commands.command(
        name="caption",
        aliases=["cap"],
        help="Add a caption above an image"
    )
    async def write_caption(self, ctx: commands.Context, *, caption: str):
        """
        Add a caption above an image or GIF.
        
        **Parameters:**
        - `caption`: The text to add as a caption
        
        **Supported formats:** JPG, JPEG, PNG, GIF
        
        **Usage:** 
        - `{prefix}caption This is my caption`
        - `{prefix}cap me when`
        
        **Note:** Attach an image or reply to a message with an image.
        """
        if not caption.strip():
            embed = discord.Embed(
                title="❌ Missing Caption",
                description="Please provide a caption for the image.",
                color=discord.Color.red()
            )
            embed.add_field(
                name="Example",
                value=f"`{ctx.prefix}caption This is my caption`",
                inline=False
            )
            await safe_send(ctx, embed=embed)
            return

        # Show processing message
        processing_embed = discord.Embed(
            title="🔄 Processing...",
            description="Adding caption to your image, please wait...",
            color=discord.Color.blue()
        )
        processing_msg = await safe_send(ctx, embed=processing_embed)

        try:
            # Try to get image attachment
            img_attachment = await get_attachment(
                ctx.message, 
                ["image/jpeg", "image/jpg", "image/png"]
            )
            
            if img_attachment:
                async with self.bot.http_session.get(img_attachment.url) as response:
                    if response.status == 200:
                        img_bytes = BytesIO(await response.read())
                        img = PILImage.open(img_bytes)
                        
                        # Delete processing message
                        if processing_msg:
                            await processing_msg.delete()
                        
                        await caption_image(
                            ctx, img, img_attachment.width,
                            img_attachment.height, caption
                        )
                        return
            
            # Try to get GIF attachment
            gif_attachment = await get_attachment(ctx.message, "image/gif")
            
            if gif_attachment:
                async with self.bot.http_session.get(gif_attachment.url) as response:
                    if response.status == 200:
                        gif_bytes = BytesIO(await response.read())
                        gif_img = PILImage.open(gif_bytes)
                        
                        # Delete processing message
                        if processing_msg:
                            await processing_msg.delete()
                        
                        await caption_gif(
                            ctx, ImageSequence.Iterator(gif_img),
                            gif_attachment.width, gif_attachment.height, caption
                        )
                        return
            
            # No attachment found
            error_embed = discord.Embed(
                title="❌ No Image Found",
                description="Please attach an image or reply to a message with an image.",
                color=discord.Color.red()
            )
            error_embed.add_field(
                name="Supported Formats",
                value="JPG, JPEG, PNG, GIF",
                inline=False
            )
            
            if processing_msg:
                await processing_msg.edit(embed=error_embed)
            else:
                await safe_send(ctx, embed=error_embed)
                
        except Exception as e:
            logger.error(f"Error in caption command: {e}")
            error_embed = discord.Embed(
                title="❌ Processing Error",
                description="An error occurred while processing your image.",
                color=discord.Color.red()
            )
            
            if processing_msg:
                await processing_msg.edit(embed=error_embed)
            else:
                await safe_send(ctx, embed=error_embed)

async def setup(bot: ChezziBot):
    """Set up the Media cog."""
    await bot.add_cog(Media(bot))
