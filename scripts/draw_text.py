# -*- coding: utf-8 -*-
"""
Renders each slide of Persian text (from output/slides.json) as its own
transparent PNG overlay — same pixel size as the video, mostly transparent
except for a semi-transparent dark panel and the text. combine.py later
overlays each one on top of the (moving/zooming) background video during
its own time window, so the TEXT stays perfectly still while only the
background moves underneath it.

Persian requires "reshaping" (joining letter forms) and bidi reordering
before PIL can draw it correctly — plain PIL text drawing renders Arabic
script letters disconnected and in the wrong order.
"""

import os
import json
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

SLIDES_PATH = "output/slides.json"
CANVAS_SIZE = (1080, 1920)  # must match the video resolution used in make_loop.py

# fonts-farsiweb package provides these — first one found wins.
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/farsiweb/Roya.ttf",
    "/usr/share/fonts/truetype/farsiweb/Nazli.ttf",
    "/usr/share/fonts/truetype/farsiweb/Elham.ttf",
    "/usr/share/fonts/truetype/farsiweb/Homa.ttf",
]
FONT_SIZE = 62
LINE_SPACING = 18
PANEL_PADDING = 60
TEXT_COLOR = (255, 255, 255, 255)
PANEL_COLOR = (0, 0, 0, 150)
WRAP_CHARS = 20  # rough characters per line before wrapping within a slide


def find_font() -> str:
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        "No Persian-capable font found. Install the 'fonts-farsiweb' apt "
        "package in the workflow before running this script."
    )


def shape_persian(text: str) -> str:
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def wrap_persian(text: str, width: int) -> list:
    words = text.split(" ")
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > width and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def render_slide(text: str, font: ImageFont.FreeTypeFont, output_path: str):
    overlay = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    raw_lines = wrap_persian(text, WRAP_CHARS)
    shaped_lines = [shape_persian(line) for line in raw_lines]

    line_heights = [draw.textbbox((0, 0), line, font=font)[3] for line in shaped_lines]
    total_text_height = sum(line_heights) + LINE_SPACING * (len(shaped_lines) - 1)

    panel_top = (CANVAS_SIZE[1] - total_text_height) // 2 - PANEL_PADDING
    panel_bottom = (CANVAS_SIZE[1] + total_text_height) // 2 + PANEL_PADDING
    draw.rectangle([(0, panel_top), (CANVAS_SIZE[0], panel_bottom)], fill=PANEL_COLOR)

    y = (CANVAS_SIZE[1] - total_text_height) // 2
    for line, line_height in zip(shaped_lines, line_heights):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        x = (CANVAS_SIZE[0] - line_width) // 2
        draw.text((x, y), line, font=font, fill=TEXT_COLOR)
        y += line_height + LINE_SPACING

    overlay.save(output_path)


def main():
    with open(SLIDES_PATH, "r", encoding="utf-8") as f:
        slides = json.load(f)

    font_path = find_font()
    font = ImageFont.truetype(font_path, FONT_SIZE)

    for i, slide_text in enumerate(slides):
        output_path = f"output/slide_{i}.png"
        render_slide(slide_text, font, output_path)
        print(f"Saved {output_path}")

    print(f"Rendered {len(slides)} slide overlays using font: {font_path}")


if __name__ == "__main__":
    main()
