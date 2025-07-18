"""Enhanced image text utilities with better error handling and modern features."""

from __future__ import annotations
from typing import Optional, Tuple, Union
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import config
from logger import logger

class ImageText:
    """Enhanced image text processor with better error handling."""
    
    def __init__(
        self, 
        filename_or_size_or_image: Union[str, Path, Tuple[int, int], Image.Image],
        mode: str = 'RGBA',
        background: Tuple[int, int, int, int] = (0, 0, 0, 0)
    ):
        """
        Initialize ImageText with various input types.
        
        Args:
            filename_or_size_or_image: Path to image, size tuple, or PIL Image
            mode: Image mode (default: RGBA)
            background: Background color tuple (default: transparent)
        """
        if isinstance(filename_or_size_or_image, (str, Path)):
            self.filename = str(filename_or_size_or_image)
            self.image = Image.open(self.filename)
            self.size = self.image.size
        elif isinstance(filename_or_size_or_image, (list, tuple)) and len(filename_or_size_or_image) == 2:
            self.size = filename_or_size_or_image
            self.image = Image.new(mode, self.size, color=background)
            self.filename = None
        elif isinstance(filename_or_size_or_image, Image.Image):
            self.image = filename_or_size_or_image
            self.size = self.image.size
            self.filename = None
        else:
            raise ValueError("Invalid input type for ImageText")

        self.draw = ImageDraw.Draw(self.image)

    def save(self, filename: Optional[str] = None, **kwargs):
        """Save the image to a file."""
        self.image.save(filename or self.filename, **kwargs)

    def show(self):
        """Display the image."""
        self.image.show()

    def get_text_size(self, font_filename: str, font_size: int, text: str) -> Tuple[int, int]:
        """Get the size of text with given font and size."""
        try:
            font = ImageFont.truetype(font_filename, font_size)
            # Use textbbox for better compatibility with newer Pillow versions
            bbox = self.draw.textbbox((0, 0), text, font=font)
            return (bbox[2] - bbox[0], bbox[3] - bbox[1])
        except OSError:
            # Fallback to default font if custom font fails
            logger.warning(f"Could not load font {font_filename}, using default")
            font = ImageFont.load_default()
            bbox = self.draw.textbbox((0, 0), text, font=font)
            return (bbox[2] - bbox[0], bbox[3] - bbox[1])

    def get_font_size(
        self, 
        text: str, 
        font: str, 
        max_width: Optional[int] = None, 
        max_height: Optional[int] = None
    ) -> int:
        """Get the maximum font size that fits within the given constraints."""
        if max_width is None and max_height is None:
            raise ValueError('You need to pass max_width or max_height')
        
        font_size = 1
        while True:
            text_size = self.get_text_size(font, font_size, text)
            if (max_width is not None and text_size[0] > max_width) or \
               (max_height is not None and text_size[1] > max_height):
                return max(1, font_size - 1)
            font_size += 1
            
            # Prevent infinite loop
            if font_size > 500:
                break
                
        return font_size

    def write_text(
        self,
        xy: Tuple[Union[int, str], Union[int, str]],
        text: str,
        font_filename: str,
        font_size: int = 11,
        color: Tuple[int, int, int] = (255, 255, 255),
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        stroke_width: int = 0,
        stroke_fill: Tuple[int, int, int] = (0, 0, 0)
    ) -> Tuple[int, int]:
        """Write text on the image."""
        x, y = xy
        
        if font_size == 'fill' and (max_width is not None or max_height is not None):
            font_size = self.get_font_size(text, font_filename, max_width, max_height)
        
        text_size = self.get_text_size(font_filename, font_size, text)
        
        try:
            font = ImageFont.truetype(font_filename, font_size)
        except OSError:
            logger.warning(f"Could not load font {font_filename}, using default")
            font = ImageFont.load_default()
        
        if x == 'center':
            x = (self.size[0] - text_size[0]) // 2
        if y == 'center':
            y = (self.size[1] - text_size[1]) // 2
        
        self.draw.text(
            (x, y), text, font=font, fill=color,
            stroke_fill=stroke_fill, stroke_width=stroke_width
        )
        
        return text_size

    def get_suitable_font_size(
        self,
        text: str,
        box_width: int,
        font_filename: str,
        line_spacing: float = 1.1
    ) -> int:
        """Get a suitable font size for text that fits in a box."""
        font_size = 8
        jump_size = 32
        words = text.split()
        lower_bound = 0.1
        upper_bound = 0.2

        while jump_size >= 1:
            lines = []
            line = []
            
            for word in words:
                new_line = ' '.join(line + [word])
                size = self.get_text_size(font_filename, font_size, new_line)
                
                if size[0] <= box_width:
                    line.append(word)
                else:
                    if line:
                        lines.append(line)
                    line = [word]
            
            if line:
                lines.append(line)

            if not lines:
                break

            text_height = size[1] * line_spacing
            total_size = len(lines) * text_height
            new_upper = upper_bound + 0.02 * len(lines)

            if lower_bound * self.size[1] <= total_size <= new_upper * self.size[1]:
                break
            elif total_size < lower_bound * self.size[1]:
                font_size += jump_size
            else:
                jump_size //= 2
                font_size = max(1, font_size - jump_size)

        return max(1, font_size)

    def write_text_box(
        self,
        xy: Tuple[int, int],
        text: str,
        box_width: int,
        font_filename: str,
        font_size: Optional[int] = None,
        color: Tuple[int, int, int] = (255, 255, 255),
        place: str = 'left',
        justify_last_line: bool = False,
        position: str = 'top',
        line_spacing: float = 1.1,
        stroke: bool = False
    ) -> Tuple[int, int]:
        """Write text in a box with word wrapping."""
        x, y = xy
        
        if font_size is None:
            font_size = self.get_suitable_font_size(
                text, box_width, font_filename, line_spacing
            )

        stroke_width = max(1, font_size // 20) if stroke else 0
        stroke_fill = (0, 0, 0) if stroke else None

        # Split text into lines
        lines = self._wrap_text(text, box_width, font_filename, font_size)
        
        if not lines:
            return (box_width, 0)

        # Calculate text height
        sample_size = self.get_text_size(font_filename, font_size, lines[0])
        text_height = sample_size[1] * line_spacing
        total_height = len(lines) * text_height

        # Calculate starting y position
        if position == 'middle':
            start_y = (self.size[1] - total_height) // 2
        elif position == 'bottom':
            start_y = self.size[1] - total_height - y
        else:
            start_y = y

        # Draw each line
        current_y = start_y
        for i, line in enumerate(lines):
            self._draw_line(
                line, x, current_y, box_width, font_filename, font_size,
                color, place, justify_last_line and i == len(lines) - 1,
                stroke_width, stroke_fill
            )
            current_y += text_height

        return (box_width, current_y - start_y)

    def _wrap_text(self, text: str, box_width: int, font_filename: str, font_size: int) -> list[str]:
        """Wrap text to fit within box width."""
        lines = []
        line = []
        words = text.split()

        for word in words:
            new_line = ' '.join(line + [word])
            size = self.get_text_size(font_filename, font_size, new_line)
            
            if size[0] <= box_width:
                line.append(word)
            else:
                if line:
                    lines.append(' '.join(line))
                line = [word]
        
        if line:
            lines.append(' '.join(line))

        return lines

    def _draw_line(
        self,
        line: str,
        x: int,
        y: int,
        box_width: int,
        font_filename: str,
        font_size: int,
        color: Tuple[int, int, int],
        place: str,
        justify: bool,
        stroke_width: int,
        stroke_fill: Optional[Tuple[int, int, int]]
    ):
        """Draw a single line of text."""
        if place == 'left':
            self.write_text(
                (x, y), line, font_filename, font_size, color,
                stroke_width=stroke_width, stroke_fill=stroke_fill
            )
        elif place == 'right':
            text_size = self.get_text_size(font_filename, font_size, line)
            x_pos = x + box_width - text_size[0]
            self.write_text(
                (x_pos, y), line, font_filename, font_size, color,
                stroke_width=stroke_width, stroke_fill=stroke_fill
            )
        elif place == 'center':
            text_size = self.get_text_size(font_filename, font_size, line)
            x_pos = x + (box_width - text_size[0]) // 2
            self.write_text(
                (x_pos, y), line, font_filename, font_size, color,
                stroke_width=stroke_width, stroke_fill=stroke_fill
            )
        elif place == 'justify' and justify:
            self._draw_justified_line(
                line, x, y, box_width, font_filename, font_size, color,
                stroke_width, stroke_fill
            )
        else:
            self.write_text(
                (x, y), line, font_filename, font_size, color,
                stroke_width=stroke_width, stroke_fill=stroke_fill
            )

    def _draw_justified_line(
        self,
        line: str,
        x: int,
        y: int,
        box_width: int,
        font_filename: str,
        font_size: int,
        color: Tuple[int, int, int],
        stroke_width: int,
        stroke_fill: Optional[Tuple[int, int, int]]
    ):
        """Draw a justified line of text."""
        words = line.split()
        if len(words) <= 1:
            self.write_text(
                (x, y), line, font_filename, font_size, color,
                stroke_width=stroke_width, stroke_fill=stroke_fill
            )
            return

        # Calculate spacing
        line_without_spaces = ''.join(words)
        total_text_width = self.get_text_size(font_filename, font_size, line_without_spaces)[0]
        space_width = (box_width - total_text_width) / (len(words) - 1)

        # Draw words with calculated spacing
        current_x = x
        for i, word in enumerate(words):
            self.write_text(
                (current_x, y), word, font_filename, font_size, color,
                stroke_width=stroke_width, stroke_fill=stroke_fill
            )
            
            if i < len(words) - 1:
                word_size = self.get_text_size(font_filename, font_size, word)
                current_x += word_size[0] + space_width
