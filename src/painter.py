import asyncio
import io
import time
from PIL import Image
from dill import dumps

import cairosvg
import xml.etree.ElementTree as ET

import shulker as mc
from tools.pulsar import Portal
from tools.config import config


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


def get_svg(word):
    with open(f"svg/{word}.svg", "r") as file:
        svg_data = file.read()
    svg_data = svg_data.replace('fill=""', 'fill="#000000"')
    return svg_data


def generate_pixel_lists(word, random=False):
    pixel_lists = []
    root = ET.fromstring(get_svg(word))

    for idx, element in enumerate(root.iter()):
        if element.tag == "{http://www.w3.org/2000/svg}path":
            shape_svg = ET.Element(
                "svg", attrib=root.attrib, xmlns="http://www.w3.org/2000/svg"
            )
            shape_svg.append(element)

            png_data = cairosvg.svg2png(
                bytestring=ET.tostring(shape_svg),
                output_height=config.height,
                output_width=config.width,
            )
            image = Image.open(io.BytesIO(png_data))
            plist = png_to_pixel_data(image)
            if random:
                random.shuffle(plist)
            pixel_lists.append(plist)

    return pixel_lists


def get_interval(big_list):
    total_blocks_to_place = len(big_list)

    wait_time = config.drawing_finished_at_percentage / 100 * config.round_time
    interval = (wait_time - (total_blocks_to_place / 1000)) / total_blocks_to_place
    if interval < 0:
        interval = 0

    return interval if interval > 0 else 0


class Painter(Portal):
    async def on_join(self):
        await self.subscribe("gl.paint_svg", self.paint)
        await self.subscribe("gl.clear_svg", self.remove_zone)

        # await self.remove_zone()
        # await self.paint("banana")

    async def remove_zone(self):
        pos1 = config.paint_start
        pos2 = pos1.offset(x=config.width, y=config.height, z=0)
        zone = mc.BlockZone(pos1, pos2)

        f = lambda: mc.set_zone(zone, "air")
        await self.publish("mc.lambda", dumps(f))

    async def paint(self, word):
        def set_pixels(pixel_list, interval):
            start_pos = config.paint_start

            for p in pixel_list:
                pos = start_pos.offset(x=p["x"], y=config.height - p["y"], z=0)
                mc.set_block(pos, p["block"])
                time.sleep(interval)

        # get a list per path
        plists = generate_pixel_lists(word)

        # flatten plists then turn it into a list of bite-sized chunks
        big_list = sum(plists, [])
        print(len(big_list))
        n = max(1, config.paint_chunk_size)
        chunks = [big_list[i : i + n] for i in range(0, len(big_list), n)]

        interval = get_interval(big_list)

        for chunk in chunks:
            f = lambda: set_pixels(chunk, interval)
            await self.publish("mc.lambda", dumps(f))


if __name__ == "__main__":
    action = Painter()
    asyncio.run(action.run())
