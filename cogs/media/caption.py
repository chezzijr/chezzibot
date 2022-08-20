import discord
from PIL import ImageFont, Image, ImageSequence
from discord.ext import commands
from utils import ImageText, reply
from io import BytesIO


def get_font_size(text: str, width: int, height: int, img_fraction: float, font_name: str) -> int:
    fontsize = 8
    font = ImageFont.truetype(font_name, fontsize)
    breakpoint = int(img_fraction * min(height, (width + height) // 2))
    jumpsize = 64
    while True:
        if font.getsize(text)[1] < breakpoint:
            fontsize += jumpsize
        else:
            jumpsize = jumpsize // 2
            fontsize -= jumpsize
        font = ImageFont.truetype(font_name, fontsize)
        if jumpsize <= 1:
            break
    return fontsize


def get_text_size(font_filename: str, font_size: int, text: str):
    font = ImageFont.truetype(font_filename, font_size)
    return font.getsize(text)


def get_extended_height(
        text: str,
        box_width: int,
        font_filename: str,
        font_size: int,
        line_spacing: float = 1.1) -> int:
    lines = []
    line = []
    words = text.split()
    for word in words:
        new_line = ' '.join(line + [word])
        size = get_text_size(font_filename, font_size, new_line)
        if size[0] <= box_width:
            line.append(word)
        else:
            lines.append(line)
            line = [word]
    if line:
        lines.append(line)
    lines = [' '.join(line) for line in lines if line]
    return int(len(lines) * get_text_size(font_filename, font_size, new_line)[1] * line_spacing)


async def caption_image(ctx: commands.Context, image: Image.Image, width: int, height: int, text: str):
    font_name = './assets/fonts/unicode.impact.ttf'
    fontsize = get_font_size(
        text, width, height, 0.1, font_name)
    margin = min(width, height) // 30
    new_height = get_extended_height(
        text, width - 2 * margin, font_name, fontsize) + 2 * margin + height
    img = ImageText((width, new_height), background=(255, 255, 255, 255))
    img.write_text_box((margin, margin), text, width - 2 * margin,
                       font_name, fontsize, (0, 0, 0), 'center', stroke_width=0)
    img.image.paste(image, (0, new_height - height))

    with BytesIO() as img_binary:
        img.save(img_binary, format="PNG")
        img_binary.seek(0)
        await reply(ctx.message, file=discord.File(img_binary, "unknown.png"))


async def caption_gif(ctx: commands.Context, gif: ImageSequence.Iterator, width: int, height: int, text: str):
    font_name = './assets/fonts/unicode.impact.ttf'
    fontsize = get_font_size(
        text, width, height, 0.1, font_name)
    margin = min(width, height) // 30
    new_height = get_extended_height(
        text, width - 2 * margin, font_name, fontsize) + 2 * margin + height
    frames = []
    for frame in gif:
        fr = ImageText((width, new_height), background=(255, 255, 255, 255))

        fr.write_text_box((margin, margin), text, width - 2 * margin,
                          font_name, fontsize, (0, 0, 0), 'center', stroke_width=0)
        fr.image.paste(frame, (0, new_height - height))

        # https://github.com/python-pillow/Pillow/issues/3128
        b = BytesIO()
        fr.save(b, format="GIF")
        fr = Image.open(b)

        frames.append(fr)

    with BytesIO() as gif_binary:
        frames[0].save(gif_binary, format="GIF",
                       save_all=True, append_images=frames[1:], loop=0)
        gif_binary.seek(0)
        return await reply(ctx.message, file=discord.File(fp=gif_binary, filename='unknown.gif'))
