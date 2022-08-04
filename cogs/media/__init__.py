from .topbottom import handle_image, handle_gif, TopBottomFlags
from .caption import caption_gif, caption_image
from discord.ext import commands
from PIL import Image as PImg, ImageSequence as PImgSeq
from io import BytesIO
from bot import ChezziBot
from utils import reply, get_attachment

__all__ = (
    "Media",
    "setup"
)


class Media(commands.Cog):
    """
    Containing all commands relating to processing media like
    images (.jpg, .jpeg, .png, .gif), video (.mp4, wav) (coming soon)
    """

    def __init__(self, bot: ChezziBot) -> None:
        self.bot = bot
        self.visible = True

    @commands.command(name="topbottom")
    async def write_top_bottom_text(
            self,
            ctx: commands.Context,
            *,
            flags: TopBottomFlags):
        """
        >Flag<

        Add top text and bottom text to image
        Using impact unicode font
        You have to attach an image or reply to the message with the image
        Currently supporting .jpg, .jpeg, .png and .gif
        The process may take a while (cuz owner is not a image processing expert)

        Parameters
        -------
        top: Optional[str]
            The top text
        bottom: Optional[str]
            The bottom text

        Aliases
        -------
        topbottom

        Examples
        -------
        t.topbottom top: Deez bottom: Nuts
        `@ChezziBot` topbottom top: Me when bottom: Me when the
        """
        if flags.top is None and flags.bottom is None:
            return await reply(ctx.message, content="Please specify top or bottom text", delete_after=5.0)

        img = await get_attachment(ctx.message, ["image/jpeg", "image/jpg", "image/png"])
        if img is not None:
            async with self.bot.http_session.get(img.url) as resp:
                img_bytes = BytesIO(await resp.content.read())
                return await handle_image(ctx, PImg.open(img_bytes), img.width, img.height, flags.top, flags.bottom)

        gif = await get_attachment(ctx.message, "image/gif")
        if gif is not None:
            async with self.bot.http_session.get(gif.url) as resp:
                gif_bytes = BytesIO(await resp.content.read())
                gif_img = PImg.open(gif_bytes)
                return await handle_gif(ctx, PImgSeq.Iterator(gif_img), gif.width, gif.height, flags.top, flags.bottom)

        await reply(ctx.message, content=("No attachment found or unsupported format. "
                                          "Use `help media topbottom` for further information"), delete_after=5.0)

    @commands.command(name="caption", aliases=["cap"])
    async def write_caption(self, ctx: commands.Context, *, cap: str):
        """
        Add caption to picture
        Using impact unicode font
        You have to attach an image or reply to the message with the image
        Currently supporting .jpg, .jpeg, .png and .gif
        The process may take a while (cuz owner is not a image processing expert)

        Parameters
        -------
        cap: str
            The caption (as long as you want)

        Aliases
        -------
        caption, cap

        Examples
        -------
        t.cap mfw
        `@ChezziBot` caption me when your mom
        """
        if not cap:
            return await reply(ctx.message, content="Please insert caption", delete_after=5.0)

        img = await get_attachment(ctx.message, ["image/jpeg", "image/jpg", "image/png"])
        if img is not None:
            async with self.bot.http_session.get(img.url) as resp:
                img_bytes = BytesIO(await resp.content.read())
                return await caption_image(ctx, PImg.open(img_bytes), img.width, img.height, cap)

        gif = await get_attachment(ctx.message, "image/gif")
        if gif is not None:
            async with self.bot.http_session.get(gif.url) as resp:
                gif_bytes = BytesIO(await resp.content.read())
                gif_img = PImg.open(gif_bytes)
                return await caption_gif(ctx, PImgSeq.Iterator(gif_img), gif.width, gif.height, cap)

        await reply(ctx.message, content=("No attachment found or unsupported format. "
                                          "Use `help media caption` for further information"), delete_after=5.0)


async def setup(bot):
    await bot.add_cog(Media(bot))
