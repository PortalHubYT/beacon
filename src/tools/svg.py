import time
import numpy as np
import shulker as mc
import re
import os
import random
import io
import cairosvg
import xml.etree.ElementTree as ET
from PIL import Image

def get_word_list(
    character_limit=None, banned_words=None, as_filename=False, shuffle=True
):
    banned_words = banned_words if banned_words else []

    word_list = []

    ls = os.listdir("svg/")
    word_list = [f.replace(".svg", "") for f in ls]

    if character_limit:
        word_list = [
            f for f in word_list if len(re.sub(r"_\$\d+", "", f)) < character_limit
        ]

    if banned_words:
        word_list = [
            f for f in word_list if re.sub(r"_\$\d+", "", f) not in banned_words
        ]

    if shuffle:
        random.seed()
        random.shuffle(word_list)

    if as_filename:
        return [f"{f}.svg" for f in word_list]

    return word_list

def get_svg_data(filename: str, trim_opacity=False) -> str:
    filename = f"svg/{filename}"

    with open(filename, "r") as file:
        svg_data = file.read()

    if trim_opacity:
        # who remembers opacity?
        svg_data = re.sub(r"<g.[^>]*(opacity)(?<!>)[\s\S]*?\/g>", "", svg_data)

    return svg_data

def png_to_pixel_data(image: Image) -> dict[tuple[int, int]]:
    grid = {}

    width, height = image.size
    for x in range(width):
        for y in range(height):
            pixel = image.getpixel((x, y))
            if pixel == (0, 0, 0, 0):
                continue
            grid[(x, y)] = pixel
        
    return grid

def svg_to_pixel_layers(
    filename: str, height: int = 100, width: int = 100, dpi: int = 96, scale: int = 1) -> list[dict]:
    """DPI = dot per inch
    This traverses the SVG file and returns a list of layers, each layer being a dictionnary with
    """

    layers = []
    root = ET.fromstring(get_svg_data(filename))
    
    for element in root.iter():
        if element.tag != "{http://www.w3.org/2000/svg}path":
            continue

        shape_svg = ET.Element(
            "svg", attrib=root.attrib, xmlns="http://www.w3.org/2000/svg"
        )
        shape_svg.append(element)

        png_data = cairosvg.svg2png(
            bytestring=ET.tostring(shape_svg),
            dpi=dpi,
            scale=scale,
            output_height=height,
            output_width=width,
        )
        image = Image.open(io.BytesIO(png_data))
        layer = png_to_pixel_data(image)

        layers.append(layer)

    return layers

def blend_colors(
    old_pixel: tuple[int, int, int, int], new_pixel: tuple[int, int, int, int]
) -> tuple[int, int, int, int]:
    old_r, old_g, old_b, old_a = old_pixel
    r, g, b, a = new_pixel

    new_a = old_a + a - (old_a * a) // 255

    if new_a == 0:
        return (0, 0, 0, 0)

    new_r = (old_r * old_a * (255 - a) + r * a * 255) // (new_a * 255)
    new_g = (old_g * old_a * (255 - a) + g * a * 255) // (new_a * 255)
    new_b = (old_b * old_a * (255 - a) + b * a * 255) // (new_a * 255)

    return (new_r, new_g, new_b, new_a)

def process_layers(
    original_layers: list[dict], trim: bool = True, blend: bool = True, only_opaque: bool = True
) -> list[list[dict]] and dict[tuple[int, int, int, int]]:
    
    processed_layers = []
    grid = {}  # To keep track of the final color at each coordinate

    for layer in reversed(original_layers):
        new_layer = []

        for (x, y), pixel in layer.items():
            
            if only_opaque and pixel[3] < 255:
                continue
            
            if (x, y) not in grid:
                grid[(x, y)] = pixel
                new_layer.append({"x": x, "y": y, "pixel": pixel})
                continue

            old_pixel = grid[(x, y)]
            old_alpha = old_pixel[3]
            new_alpha = pixel[3]

            # Skip if the old pixel is fully opaque and we're trimming lower_layers
            if trim and old_alpha == 255:
                continue

            # Skip if the new pixel is fully transparent
            if new_alpha == 0:
                continue

            if blend:
                new_pixel = blend_colors_to_opaque(old_pixel, pixel)
            else:
                new_pixel = pixel

            if new_pixel[3] < 255:
                # Handle non-opaque pixels here. For example, blend with a background.
                new_pixel = blend_colors_to_opaque(new_pixel, (255, 255, 255, 255))

            grid[(x, y)] = new_pixel
            new_layer.append({"x": x, "y": y, "pixel": new_pixel})

        if new_layer:
            processed_layers.insert(0, new_layer)

    return processed_layers, grid

def blend_colors_to_opaque(old_pixel, new_pixel, background_color=(255, 255, 255, 255)):
    blended = blend_colors(old_pixel, new_pixel)
    if blended[3] < 255:
        return blend_colors(blended, background_color)
    return blended

def pixel_to_block(pixel: tuple[int, int, int, int], palette: dict = None):
    return mc.color_picker(pixel, palette)

def greedy_sort(layers):
    sorted_layers = []

    def distance(p1, p2):
        return abs(p1["x"] - p2["x"]) + abs(p1["y"] - p2["y"])

    for layer in layers:
        
        if not layer:
            return []

        visited = set()
        sorted = []

        # Initialize with the first point
        current_point = layer[0]
        sorted.append(current_point)
        visited.add((current_point["x"], current_point["y"]))

        while len(sorted) < len(layer):
            closest_distance = float("inf")
            closest_point = None

            for point in layer:
                point_tuple = (point["x"], point["y"])
                if point_tuple in visited:
                    continue

                dist = distance(current_point, point)
                if dist < closest_distance:
                    closest_distance = dist
                    closest_point = point

            current_point = closest_point
            sorted.append(current_point)
            visited.add((current_point["x"], current_point["y"]))

        txt = f"-> Greedy sorted layer [{len(sorted_layers) + 1}/{len(layers)}]"
        print(txt, end="\r")
        sorted_layers.append(sorted)
        
    return sorted_layers

def svg_to_block_lists(
    filename: str,
    palette: dict = None,
    dpi: int = 96,
    scale: float = 1,
    sort: str = "greedy",
    trim: bool = True,
    blend: bool = True,
    only_opaque: bool = True,
) -> dict:
    """
    Will return a data dictionnary containing:
        - layers: a list of layers, each layer being a list of pixels
        - grid: a dictionnary of the final color at each coordinate
        - block_lists: a list of block lists, each block list being a list of blocks
    """

    ################################################
    start = time.time()
    
    if filename not in get_word_list(as_filename=True):
        print(f"File {filename} not found in word list.")
        return None
    
    print(f"-> OK [{time.time() - start:.1f}s] | Filename: {filename} exists")
    ################################################
    start = time.time()
    
    if not palette:
        palette: dict[str] = mc.get_palette("side")
    
    print(f"-> OK [{time.time() - start:.1f}s] | Palette: {len(palette.items())} colors")
    ################################################
    start = time.time()
    
    layers = svg_to_pixel_layers(filename, dpi=dpi, scale=scale)
    amount_of_blocks = sum([len(layer) for layer in layers])
    
    print(f"-> OK [{time.time() - start:.1f}s] | Layers: {len(layers)} = {amount_of_blocks} blocks")
    ################################################
    start = time.time()
    
    layers, grid = process_layers(layers, trim, blend, only_opaque)
    new_amount_of_blocks = sum([len(layer) for layer in layers])
    difference = amount_of_blocks - new_amount_of_blocks
    final_amount_of_blocks = len(grid.items())
    
    print(f"-> OK [{time.time() - start:.1f}s] | Processed layers: {len(layers)} (Removed {difference} blocks) | Final grid: {final_amount_of_blocks} blocks")
    ################################################
    start = time.time()
    
    if sort == "greedy":
        layers = greedy_sort(layers)

    print(f"-> OK [{time.time() - start:.1f}s] | Sorted layers: {len(layers)}")
    ################################################
    start = time.time()
    
    block_lists = []
    for layer in layers:
        block_lists.append(
            [
                {
                    "x": pixel_info["x"],
                    "y": pixel_info["y"],
                    "block": pixel_to_block(pixel_info["pixel"], palette),
                }
                for pixel_info in layer
            ]
        )

    print(f"-> OK [{time.time() - start:.1f}s] | Transformed pixels to blocks: {sum([len(layer) for layer in block_lists])}")
    ################################################
    
    return {"layers": layers, "grid": grid, "block_list": block_lists}
