from PIL import Image, ImageDraw, ImageFont


class ImageText(object):
    def __init__(self, filename_or_size_or_Image, mode='RGBA', background=(0, 0, 0, 0)):
        if isinstance(filename_or_size_or_Image, str):
            self.filename = filename_or_size_or_Image
            self.image = Image.open(self.filename)
            self.size = self.image.size
        elif isinstance(filename_or_size_or_Image, (list, tuple)) and len(filename_or_size_or_Image) == 2:
            self.size = filename_or_size_or_Image
            self.image = Image.new(mode, self.size, color=background)
            self.filename = None
        elif isinstance(filename_or_size_or_Image, Image.Image):
            self.image = filename_or_size_or_Image
            self.size = self.image.size
            self.filename = None

        self.draw = ImageDraw.Draw(self.image)

    def save(self, filename=None, **kwargs):
        self.image.save(filename or self.filename, **kwargs)

    def show(self):
        self.image.show()

    def get_font_size(self, text: str, font: str, max_width: int = None, max_height: int = None):
        if max_width is None and max_height is None:
            raise ValueError('You need to pass max_width or max_height')
        font_size = 1
        text_size = self.get_text_size(font, font_size, text)
        if (max_width is not None and text_size[0] > max_width) or \
           (max_height is not None and text_size[1] > max_height):
            raise ValueError("Text can't be filled in only (%dpx, %dpx)" %
                             text_size)
        while True:
            if (max_width is not None and text_size[0] >= max_width) or \
               (max_height is not None and text_size[1] >= max_height):
                return font_size - 1
            font_size += 1
            text_size = self.get_text_size(font, font_size, text)

    def write_text(
            self,
            xy: tuple[int, int],
            text: str,
            font_filename: str,
            font_size: int = 11,
            color: tuple[int, int, int] = (255, 255, 255),
            max_width: int = None,
            max_height: int = None,
            stroke_width: int = 1):
        x, y = xy
        if font_size == 'fill' and \
           (max_width is not None or max_height is not None):
            font_size = self.get_font_size(text, font_filename, max_width,
                                           max_height)
        text_size = self.get_text_size(font_filename, font_size, text)
        font = ImageFont.truetype(font_filename, font_size)
        if x == 'center':
            x = (self.size[0] - text_size[0]) / 2
        if y == 'center':
            y = (self.size[1] - text_size[1]) / 2
        self.draw.text((x, y), text, font=font, fill=color,
                       stroke_fill=(0, 0, 0), stroke_width=stroke_width)
        return text_size

    def get_text_size(self, font_filename: str, font_size: int, text: str):
        font = ImageFont.truetype(font_filename, font_size)
        return font.getsize(text)

    def get_suitable_font_size(
            self,
            text: str,
            box_width: int,
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
                size = self.get_text_size(font_filename, font_size, new_line)
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

            if lower * self.size[1] <= total_size <= new_upper * self.size[1]:
                break

            elif total_size < lower * self.size[1]:
                font_size += jumpsize
            else:
                jumpsize //= 2
                font_size -= jumpsize
        return font_size

    def write_text_box(
            self,
            xy: tuple[int, int],
            text: str,
            box_width: int,
            font_filename: str,
            font_size: int = None,
            color: tuple[int, int, int] = (255, 255, 255),
            place: str = 'left',
            justify_last_line: bool = False,
            position: str = 'top',
            line_spacing: float = 1.1,
            stroke: bool = False):

        x, y = xy
        lines = []
        line = []
        words = text.split()

        if font_size is None:
            font_size = self.get_suitable_font_size(
                text, box_width, font_filename, line_spacing)

        stroke_width = font_size // 20 if stroke else 0

        for word in words:
            new_line = ' '.join(line + [word])
            size = self.get_text_size(font_filename, font_size, new_line)
            text_height = size[1] * line_spacing
            last_line_bleed = text_height - size[1]
            if size[0] <= box_width:
                line.append(word)
            else:
                lines.append(line)
                line = [word]
        if line:
            lines.append(line)
        lines = [' '.join(line) for line in lines if line]

        match position:
            case 'middle':
                height = (self.size[1] - len(lines) *
                          text_height + last_line_bleed) // 2
                height -= text_height
            case 'bottom':
                height = self.size[1] - \
                    len(lines) * text_height + last_line_bleed
                height -= y
            case _:
                height = y

        for index, line in enumerate(lines):
            match place:
                case 'left':
                    self.write_text((x, height), line, font_filename, font_size,
                                    color, stroke_width=stroke_width)
                case 'right':
                    total_size = self.get_text_size(
                        font_filename, font_size, line)
                    x_left = x + box_width - total_size[0]
                    self.write_text((x_left, height), line, font_filename,
                                    font_size, color, stroke_width=stroke_width)
                case 'center':
                    total_size = self.get_text_size(
                        font_filename, font_size, line)
                    x_left = int(x + ((box_width - total_size[0]) / 2))
                    self.write_text((x_left, height), line, font_filename,
                                    font_size, color, stroke_width=stroke_width)
                case 'justify':
                    words = line.split()
                    if (index == len(lines) - 1 and not justify_last_line) or \
                            len(words) == 1:
                        self.write_text((x, height), line, font_filename, font_size,
                                        color, stroke_width=stroke_width)
                        continue
                    line_without_spaces = ''.join(words)
                    total_size = self.get_text_size(font_filename, font_size,
                                                    line_without_spaces)
                    space_width = (
                        box_width - total_size[0]) / (len(words) - 1.0)
                    start_x = x
                    for word in words[:-1]:
                        self.write_text((start_x, height), word, font_filename,
                                        font_size, color, stroke_width=stroke_width)
                        word_size = self.get_text_size(font_filename, font_size,
                                                       word)
                        start_x += word_size[0] + space_width
                    last_word_size = self.get_text_size(font_filename, font_size,
                                                        words[-1])
                    last_word_x = x + box_width - last_word_size[0]
                    self.write_text((last_word_x, height), words[-1], font_filename,
                                    font_size, color, stroke_width=stroke_width)
                case _:
                    raise ValueError("Not correct argument \"place\"")

            height += text_height
        return (box_width, height - y)
