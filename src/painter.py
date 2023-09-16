import asyncio
import io
import time
import importlib

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

    # svg_data = svg_data.replace('fill=""', 'fill="#000000"')
    # svg_data = svg_data.replace('fill="#004364"', 'fill="#000000"')
    return svg_data


class Painter(Portal):
    async def on_join(self):
        await self.reload_config()
        self.stop_painting = False
        self.rush_paint = False
        await self.subscribe("gl.paint_svg", self.paint)
        await self.subscribe("gl.clear_svg", self.remove_zone)
        await self.subscribe("painter.stop", self.stop_painter)
        await self.subscribe("painter.create_backboard", self.create_backboard)
        await self.subscribe("painter.remove_backboard", self.remove_backboard)
        await self.subscribe("painter.move_backboard", self.move_backboard)
        await self.subscribe("gl.rush_paint", self.on_rush)
        await self.subscribe("gl.reload_config", self.reload_config)

        if not hasattr(self, "backboard_origin"):
            # await self.create_backboard()
            pass

    async def reload_config(self):
        importlib.reload(tools.config)
        self.config = tools.config.config

    def generate_pixel_lists(self, word, word_variant, random=False):
        pixel_lists = []
        root = ET.fromstring(get_svg(word, word_variant))

        for idx, element in enumerate(root.iter()):
            if element.tag == "{http://www.w3.org/2000/svg}path":
                shape_svg = ET.Element(
                    "svg", attrib=root.attrib, xmlns="http://www.w3.org/2000/svg"
                )
                shape_svg.append(element)

                png_data = cairosvg.svg2png(
                    bytestring=ET.tostring(shape_svg),
                    output_height=self.config.height,
                    output_width=self.config.width,
                )
                image = Image.open(io.BytesIO(png_data))
                plist = png_to_pixel_data(image)
                if random:
                    random.shuffle(plist)
                pixel_lists.append(plist)

        return pixel_lists

    async def on_rush(self):
        print("-> Rush painting")
        self.rush_paint = True

    async def stop_painter(self):
        self.stop_painting = True

    async def create_corner(self):
        # remove 4x4
        # place 2x4 horiz
        # place 2x4 vert
        # place last block
        pass

    async def get_interval(self, steps):
        wait_time = (
            self.config.drawing_finished_at_percentage / 100 * self.config.round_time
        )
        interval = (wait_time - (steps / 10)) / steps
        interval = interval if interval > 0 else 0
        if interval > 0.75:
            interval = 0.75

        print(
            f"Try {wait_time}: ({(steps / 10)}s to build) + ({steps} steps x {interval:.2f} = {steps*interval}s)"
        )
        return interval

    async def move_backboard(self):
        await self.reload_config()

        if hasattr(self, "backboard_origin"):
            print("-> Move backboard")
            await self.remove_backboard(self.backboard_origin)
            await self.create_backboard()

    async def create_backboard(self):
        print("-> Create backboard")
        origin = self.config.paint_start.offset(z=-2)

        # black backboard
        pos1 = origin.offset(x=-8, y=-3)
        pos2 = origin.offset(x=self.config.width + 8, y=self.config.height + 3)
        zone = mc.BlockZone(pos1, pos2)
        f = lambda: mc.set_zone(zone, "black_concrete")
        await self.publish("mc.lambda", dumps(f))

        # white canvas
        canvas_pos1 = pos1.offset(x=2, y=2)
        canvas_pos2 = pos2.offset(x=-2, y=-2)
        zone = mc.BlockZone(canvas_pos1, canvas_pos2)
        f = lambda: mc.set_zone(zone, "snow_block")
        await self.publish("mc.lambda", dumps(f))

        # corners

        # lights
        light_pos1 = pos1.offset(z=3)
        light_pos2 = pos2.offset(z=3)
        zone = mc.BlockZone(light_pos1, light_pos2)
        f = lambda: mc.set_zone(zone, "light")
        await self.call("mc.lambda", dumps(f))

        self.backboard_origin = origin

    async def remove_backboard(self, start=None):
        if start:
            base_origin = self.config.paint_start
        else:
            base_origin = start

        print("-> Remove backboard")
        origin = base_origin.offset(z=-2)
        pos1 = origin.offset(x=-8, y=-3)
        pos2 = origin.offset(x=self.config.width + 8, y=self.config.height + 3)

        zone = mc.BlockZone(pos1, pos2)
        f = lambda: mc.set_zone(zone, "air")
        await self.publish("mc.lambda", dumps(f))

        light_pos1 = pos1.offset(z=3)
        light_pos2 = pos2.offset(z=3)

        zone = mc.BlockZone(light_pos1, light_pos2)
        f = lambda: mc.set_zone(zone, "air")
        await self.publish("mc.lambda", dumps(f))

    async def remove_zone(self):
        pos1 = self.config.paint_start
        pos2 = pos1.offset(x=self.config.width, y=self.config.height, z=0)
        zone = mc.BlockZone(pos1, pos2)

        f = lambda: mc.set_zone(zone, "air")
        await self.publish("mc.lambda", dumps(f))

    async def paint(self, data):
        word, word_variant = data

        self.stop_painting = False
        self.rush_paint = False

        def paint_chunk(height, start_pos, pixel_list):
            for p in pixel_list:
                pos = start_pos.offset(x=p["x"], y=height - p["y"], z=0)
                mc.set_block(pos, p["block"])

        # get a list per path
        plists = self.generate_pixel_lists(word, word_variant)

        # flatten plists then turn it into a list of bite-sized chunks
        big_list = sum(plists, [])
        n = max(1, self.config.paint_chunk_size)
        chunks = [big_list[i : i + n] for i in range(0, len(big_list), n)]

        interval = await self.get_interval(len(chunks))

        print(f"Painting '{word}': {len(big_list)} blocks")
        start = time.time()

        start_pos = self.config.paint_start
        height = self.config.height

        for chunk in chunks:
            if not self.rush_paint:
                await asyncio.sleep(interval)

            f = lambda: paint_chunk(height, start_pos, chunk)
            await self.publish("mc.lambda", dumps(f))
            if self.stop_painting:
                break

        self.rush_paint = False
        await self.publish("painter.finished")
        print(f"Finished in {str(time.time() - start)[:2]} seconds\n")


if __name__ == "__main__":
    action = Painter()
    while True:
        try:
            asyncio.run(action.run())
        except Exception as e:
            error_msg = f"An error occurred: {e}"
            print(error_msg)
            print("-> Restarting in 1 seconds...")
            time.sleep(1)
