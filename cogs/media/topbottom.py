from typing import Optional
import discord
from discord.ext import commands
from PIL import (
    Image as PImg,
    ImageFont as PImgFont,
    ImageSequence as PImgSeq
)
from io import BytesIO
from utils import reply, ImageText


class TopBottomFlags(commands.FlagConverter):
    top: Optional[str]
    bottom: Optional[str]


def get_text_size(font_filename: str, font_size: int, text: str):
    font = PImgFont.truetype(font_filename, font_size)
    bbox = font.getbbox(text)
    return (bbox[2] - bbox[0], bbox[3] - bbox[1])

def get_suitable_font_size(
        text: str,
        box_width: int,
        img_height: int,
        font_filename: str,
        line_spacing: float = 1.1) -> int:

    font_size = 8
    jumpsize = 32
    words = text.split()
    lower = 0.1
    upper = 0.2

    while True:
        lines = []
        line = []
        for word in words:
            new_line = ' '.join(line + [word])
            size = get_text_size(font_filename, font_size, new_line)
            text_height = size[1] * line_spacing
            if size[0] <= box_width:
                line.append(word)
            else:
                lines.append(line)
                line = [word]
        if line:
            lines.append(line)

        total_size = len(lines) * text_height
        new_upper = upper + 0.02 * len(lines)

        if lower * img_height <= total_size <= new_upper * img_height:
            break

        elif total_size < lower * img_height:
            font_size += jumpsize
        else:
            jumpsize //= 2
            font_size -= jumpsize
    return font_size


async def handle_image(
        ctx: commands.Context,
        img: PImg.Image,
        width: int,
        height: int,
        top_text: Optional[str] = None,
        bottom_text: Optional[str] = None):
    margin = min(width, height) // 30
    image = ImageText(img)

    # Write top text
    if top_text:
        image.write_text_box((margin, margin), top_text, width - 2 * margin,
                             './assets/fonts/unicode.impact.ttf', place='center', stroke=True)

    # Write bottom text
    if bottom_text:
        image.write_text_box((margin, margin), bottom_text, width - 2 * margin,
                             './assets/fonts/unicode.impact.ttf', place='center', position='bottom', stroke=True)
    with BytesIO() as image_binary:
        image.image.save(image_binary, format='PNG')
        image_binary.seek(0)
        return await reply(ctx.message, file=discord.File(fp=image_binary, filename='unknown.png'))


async def handle_gif(
        ctx: commands.Context,
        gif: PImgSeq.Iterator,
        width: int,
        height: int,
        top_text: Optional[str] = None,
        bottom_text: Optional[str] = None):
    frames: list[PImg.Image] = []
    margin = min(width, height) // 30
    top_font_size = None
    bottom_font_size = None
    for frame in gif:
        fr = ImageText(frame.convert('RGBA'))

        if top_font_size is None and top_text:
            top_font_size = fr.get_suitable_font_size(
                top_text, width - 2 * margin, './assets/fonts/unicode.impact.ttf')

        if bottom_font_size is None and bottom_text:
            bottom_font_size = fr.get_suitable_font_size(
                bottom_text, width - 2 * margin, './assets/fonts/unicode.impact.ttf')

        if top_text:
            fr.write_text_box((margin, margin), top_text, width -
                              2 * margin, './assets/fonts/unicode.impact.ttf', top_font_size, place='center', stroke=True)

        if bottom_text:
            fr.write_text_box((margin, margin), bottom_text, width -
                              2 * margin, './assets/fonts/unicode.impact.ttf', bottom_font_size, place='center', position='bottom', stroke=True)

        # https://github.com/python-pillow/Pillow/issues/3128
        b = BytesIO()
        fr.save(b, format="GIF")
        fr = PImg.open(b)

        frames.append(fr)

    with BytesIO() as gif_binary:
        frames[0].save(gif_binary, format="GIF",
                       save_all=True, append_images=frames[1:], loop=0)
        gif_binary.seek(0)
        return await reply(ctx.message, file=discord.File(fp=gif_binary, filename='unknown.gif'))
