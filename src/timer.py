import asyncio
import time
import importlib
import shulker as mc
from dill import dumps
import copy

import tools.config
from tools.pulsar import Portal


class Timer(Portal):
    async def on_join(self):
        await self.reload_config()

        await self.subscribe("gl.reload_config", self.reload_config)
        await self.subscribe("timer.set", self.set_timer)
        await self.subscribe("timer.reset", self.reset_timer)
        await self.subscribe("timer.build", self.build_timer)
        await self.subscribe("timer.remove", self.remove_timer)
        await self.subscribe("timer.reload", self.reload_timer)
        await self.initialize_timer()

    async def draw_progress_bar(self, value, draw=False):
        def draw_lambda(origin, lines):
            for x in range(len(lines[0])):
                for y in range(len(lines)):
                    pos = origin.offset(x=x, y=y, z=-1)
                    mc.set_block(pos, lines[y][x])

        origin = self.config.timer_start.offset(
            x=self.config.timer_border_thickness, y=self.config.timer_border_thickness
        )
        palette = self.config.timer_palette
        width = (
            self.config.width
            + self.config.backboard_extra_size * 2
            + self.config.timer_border_thickness
        )
        height = self.config.timer_height + 1  # whi + 1 ? Idk

        if draw:
            lines = [[] for _ in range(height)]
            for y in range(height):
                while len(lines[y]) <= width:
                    block = self.config.timer_palette[
                        (len(lines[y]) + y) % len(palette)
                    ]
                    lines[y].append(block)

            if value < 100:
                bar_x = int(width * (value / 100))
                for y in range(height):
                    lines[y][bar_x] = "black_concrete"
                white_x = bar_x + 1
                for x in range(width - white_x):
                    for y in range(height):
                        lines[y][x + white_x] = "snow_block"

            f = lambda: draw_lambda(origin, lines)
            await self.publish("mc.lambda", dumps(f))
        else:
            pos1 = origin.offset(x=int(width * (value / 100)), z=-1)
            pos2 = origin.offset(x=width, y=height - 1, z=-1)
            zone = mc.BlockZone(pos1, pos2)

            f = lambda: mc.set_zone(zone, "snow_block")
            await self.publish("mc.lambda", dumps(f))

            zone = mc.BlockZone(pos1, pos1.offset(y=height - 1))
            f = lambda: mc.set_zone(zone, "black_concrete")
            await self.publish("mc.lambda", dumps(f))

    async def reload_timer(self):
        await self.remove_timer()
        await self.reload_config()
        await self.build_timer()

    async def remove_timer(self):
        print("-> Remove timer")
        height = self.config.timer_height + self.config.timer_border_thickness * 2 + 30
        width = (
            self.config.width
            + self.config.backboard_extra_size * 2
            + self.config.timer_border_thickness * 2
        )
        pos1 = self.config["timer_start"]
        pos2 = pos1.offset(x=width, y=height, z=-1)
        remove_zone = mc.BlockZone(pos1, pos2)

        f = lambda: mc.set_zone(remove_zone, "air")
        await self.publish("mc.lambda", dumps(f))

    async def build_timer(self):
        print("-> Build timer")
        height = self.config.timer_height + self.config.timer_border_thickness * 2
        width = (
            self.config.width
            + self.config.backboard_extra_size * 2
            + self.config.backboard_border_thickness * 2
        )

        # background
        pos1 = self.config["timer_start"]
        pos2 = pos1.offset(x=width, y=height)
        borders = mc.BlockZone(pos1, pos2)

        f = lambda: mc.set_zone(borders, "black_concrete")
        await self.publish("mc.lambda", dumps(f))

        # cutout
        cutout_pos1 = pos1.offset(
            x=self.config.timer_border_thickness,
            y=self.config.timer_border_thickness,
        )
        cutout_pos2 = pos1.offset(
            x=width - self.config.timer_border_thickness,
            y=height - self.config.timer_border_thickness,
        )
        cutout_zone = mc.BlockZone(cutout_pos1, cutout_pos2)
        f = lambda: mc.set_zone(cutout_zone, "air")
        await self.publish("mc.lambda", dumps(f))

        # background
        background_pos1 = cutout_pos1.offset(z=-1)
        background_pos2 = cutout_pos2.offset(z=-1)
        background_zone = mc.BlockZone(background_pos1, background_pos2)
        f = lambda: mc.set_zone(background_zone, "snow_block")
        await self.publish("mc.lambda", dumps(f))

        # lights
        lights_pos1 = cutout_pos1.offset(z=1)
        lights_pos2 = cutout_pos2.offset(z=1)
        lights_zone = mc.BlockZone(lights_pos1, lights_pos2)

        f = lambda: mc.set_zone(lights_zone, "light")
        await self.publish("mc.lambda", dumps(f))

        # corners
        bottom_left = [
            mc.BlockZone(pos1, pos1.offset(x=1, y=1)),
            mc.BlockZone(pos1, pos1.offset(x=3)),
            mc.BlockZone(pos1, pos1.offset(y=3)),
        ]
        top_left = [
            mc.BlockZone(pos1.offset(y=height), pos1.offset(x=1, y=height - 1)),
            mc.BlockZone(pos1.offset(y=height), pos1.offset(x=3, y=height)),
            mc.BlockZone(pos1.offset(y=height), pos1.offset(y=height - 3)),
        ]
        bottom_right = [
            mc.BlockZone(pos1.offset(x=width), pos1.offset(x=width - 1, y=1)),
            mc.BlockZone(pos1.offset(x=width), pos1.offset(x=width - 3)),
            mc.BlockZone(pos1.offset(x=width), pos1.offset(x=width, y=3)),
        ]
        top_right = [
            mc.BlockZone(
                pos1.offset(x=width, y=height), pos1.offset(x=width - 1, y=height - 1)
            ),
            mc.BlockZone(
                pos1.offset(x=width, y=height), pos1.offset(x=width - 3, y=height)
            ),
            mc.BlockZone(
                pos1.offset(x=width, y=height), pos1.offset(x=width, y=height - 3)
            ),
        ]

        def transpose_angle(zones, x, y):
            new_zones = []
            for z in zones:
                new_zones.append(
                    mc.BlockZone(z.pos1.offset(x=x, y=y), z.pos2.offset(x=x, y=y))
                )
            return new_zones

        voids = [
            bottom_left,
            top_left,
            bottom_right,
            top_right,
        ]
        fills = [
            transpose_angle(bottom_left, 2, 2),
            transpose_angle(top_left, 2, -2),
            transpose_angle(bottom_right, -2, 2),
            transpose_angle(top_right, -2, -2),
        ]
        for void_zones, fill_zones in zip(voids, fills):
            for v_zone, f_zone in zip(void_zones, fill_zones):
                f = lambda: mc.set_zone(v_zone, "air")
                await self.publish("mc.lambda", dumps(f))
                f = lambda: mc.set_zone(f_zone, "black_concrete")
                await self.publish("mc.lambda", dumps(f))

        await self.draw_progress_bar(100, draw=True)

    async def reload_config(self):
        importlib.reload(tools.config)
        self.config = tools.config.config

    async def initialize_timer(self):
        print("-> Initializing timer")

    async def reset_timer(self):
        print("-> Reset timer")
        await self.draw_progress_bar(100, draw=True)

    async def set_timer(self, value):
        print("-> Setting timer to", value)
        await self.draw_progress_bar(value)


if __name__ == "__main__":
    action = Timer()
    while True:
        try:
            asyncio.run(action.run(), debug=True)
        except Exception as e:
            error_msg = f"An error occurred: {e}"
            print(error_msg)
            print("-> Restarting in 1 seconds...")
            time.sleep(1)
