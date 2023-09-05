import asyncio
from dill import dumps
import io
from PIL import Image


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
                    {"x": -x, "y": -y, "block": mc.color_picker(pixel, palette)}
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


class Painter(Portal):
    async def on_join(self):
        await self.subscribe("gl.painter", self.paint)
        await self.paint("banana")

    async def paint(self, word):
        def set_pixels(plists):
            print("enter setpixels")
            start_pos = config.camera_pos.offset(x=int(config.width / 2), y=10, z=-100)
            for plist in plists:
                for p in plist:
                    print("putpixel?")
                    pos = start_pos.offset(x=p["x"], y=p["y"], z=0)

                    print(mc.set_block(pos, p["block"]))

        plists = generate_pixel_lists(word)

        print("heu ouais go paint")
        f = lambda: set_pixels(plists)
        await self.publish("mc.lambda", dumps(f))


if __name__ == "__main__":
    action = Painter()
    asyncio.run(action.run())
