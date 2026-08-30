"""
Draws the fact text (from output/fact.txt) on top of the background image
(output/image.png), with a semi-transparent dark panel behind the text for
readability. Saves the result as output/image_with_text.png, which is what
make_loop.py turns into the zooming video.
"""

import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

IMAGE_PATH = "output/image.png"
FACT_PATH = "output/fact.txt"
OUTPUT_PATH = "output/image_with_text.png"

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE = 64
WRAP_WIDTH = 22          # characters per line, tuned for FONT_SIZE at 1024px width
LINE_SPACING = 16
PANEL_PADDING = 60
TEXT_COLOR = (255, 255, 255, 255)
PANEL_COLOR = (0, 0, 0, 140)  # semi-transparent black


def main():
    with open(FACT_PATH, "r", encoding="utf-8") as f:
        fact = f.read().strip()

    image = Image.open(IMAGE_PATH).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    lines = textwrap.wrap(fact, width=WRAP_WIDTH)

    line_heights = [draw.textbbox((0, 0), line, font=font)[3] for line in lines]
    total_text_height = sum(line_heights) + LINE_SPACING * (len(lines) - 1)

    panel_top = (image.height - total_text_height) // 2 - PANEL_PADDING
    panel_bottom = (image.height + total_text_height) // 2 + PANEL_PADDING
    draw.rectangle([(0, panel_top), (image.width, panel_bottom)], fill=PANEL_COLOR)

    y = (image.height - total_text_height) // 2
    for line, line_height in zip(lines, line_heights):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        x = (image.width - line_width) // 2
        draw.text((x, y), line, font=font, fill=TEXT_COLOR)
        y += line_height + LINE_SPACING

    combined = Image.alpha_composite(image, overlay).convert("RGB")
    combined.save(OUTPUT_PATH)
    print(f"Saved image with text to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
