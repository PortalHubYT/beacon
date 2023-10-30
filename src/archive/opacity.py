import asyncio
import io
import time
import importlib
import random

from PIL import Image
from dill import dumps

import cairosvg
import xml.etree.ElementTree as ET

import shulker as mc
from tools.pulsar import Portal
import tools.config


def png_to_pixel_data(image):
    palette = mc.get_palette("side")
    pixel_data = []

    width, height = image.size
    for x in range(width):
        for y in range(height):
            pixel = image.getpixel((x, y))
            if pixel[3] > 0:
                pixel_data.append(
                    {"x": x, "y": y, "block": mc.color_picker(pixel, palette)}
                )
    return pixel_data


def get_svg(word, word_variant):
    if not word_variant:
        filename = f"svg/{word}.svg"
    else:
        filename = f"svg/{word}_${word_variant}.svg"

    with open(filename, "r") as file:
        svg_data = file.read()

    return svg_data


def main():
    word = "waterfall"
    word_variant = None
    pixel_lists = []
    root = ET.fromstring(get_svg(word, word_variant))
    for idx, element in enumerate(root.iter()):
        shape_svg = ET.Element(
            "svg", attrib=root.attrib, xmlns="http://www.w3.org/2000/svg"
        )
        if element.tag == "{http://www.w3.org/2000/svg}path":
            shape_svg.append(element)

            png_data = cairosvg.svg2png(
                bytestring=ET.tostring(shape_svg),
                output_height=100,
                output_width=100,
            )
            image = Image.open(io.BytesIO(png_data))
            plist = png_to_pixel_data(image)
            if random:
                random.shuffle(plist)
            pixel_lists.append(plist)

    return pixel_lists


main()
