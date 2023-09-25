import asyncio
import time
import importlib

from dill import dumps
import shulker as mc

from tools.pulsar import Portal
from tools.svg import svg_to_block_lists
import tools.config


class Painter(Portal):
    
    async def on_join(self):
        
        await self.reload_config()

        self.stop_painting = False
        self.rush_paint = False
        self.fast_mode = False
        self.computed_svg = None

        await self.subscribe("gl.paint_svg", self.paint)
        await self.subscribe("gl.clear_svg", self.remove_zone)
        await self.subscribe("painter.stop", self.stop_painter)
        await self.subscribe("painter.create_backboard", self.create_backboard)
        await self.subscribe("painter.remove_backboard", self.remove_backboard)
        await self.subscribe("painter.reload_backboard", self.reload_backboard)
        await self.subscribe("gl.rush_paint", self.on_rush)
        await self.subscribe("gl.reload_config", self.reload_config)
        await self.subscribe("painter.fast_mode", self.toggle_fast_mode)
        await self.subscribe("painter.compute_svg", self.compute_svg)

        await self.publish("painter.joined")

        self.is_computing = False
        self.is_painting = False
        await self.wait_loop()

    async def wait_loop(self):
        i = 0
        while True:
            await asyncio.sleep(1)
            if not self.is_computing and not self.is_painting:
                i += 1
                print(
                    f"-> Painter is idle (not computing, not painting) [{i}s]",
                    end="\r",
                    flush=True,
                )
            else:
                i = 0

    async def reload_config(self):
        importlib.reload(tools.config)
        self.config = tools.config.config

    async def toggle_fast_mode(self):
        self.fast_mode = not self.fast_mode

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
        interval = (wait_time - (steps / (1000 / self.config.paint_chunk_size))) / steps
        interval = interval if interval > 0 else 0
        if interval > 0.75:
            interval = 0.75

        return interval, wait_time, steps

    async def reload_backboard(self):
        print("-> Reload backboard")
        await self.remove_backboard()
        await self.reload_config()
        await self.create_backboard()

    async def create_backboard(self):
        print("-> Create backboard")
        origin = self.config.paint_start.offset(z=-2)
        extra_margin = self.config.backboard_extra_size
        extra_height = self.config.backboard_extra_height
        border_thickness = self.config.backboard_border_thickness

        height = (
            self.config.height + extra_margin * 2 + border_thickness * 2 + extra_height
        )
        width = self.config.width + extra_margin * 2 + border_thickness * 2
        print(f"1-{height=}{width=}")
        # black backboard
        pos1 = origin.offset(
            x=-extra_margin - border_thickness, y=-extra_margin - border_thickness
        )
        pos2 = pos1.offset(x=width, y=height)
        zone = mc.BlockZone(pos1, pos2)
        f = lambda: mc.set_zone(zone, "black_concrete")
        await self.publish("mc.lambda", dumps(f))

        # white canvas
        canvas_pos1 = pos1.offset(x=border_thickness, y=border_thickness)
        canvas_pos2 = pos2.offset(x=-border_thickness, y=-border_thickness)
        zone = mc.BlockZone(canvas_pos1, canvas_pos2)
        f = lambda: mc.set_zone(zone, "snow_block")
        await self.publish("mc.lambda", dumps(f))

        # painting zone
        # painting1 = origin
        # painting2 = origin.offset(x=self.config.width, y=self.config.height)
        # zone = mc.BlockZone(painting1, painting2)
        # f = lambda: mc.set_zone(zone, "stone")
        # await self.publish("mc.lambda", dumps(f))

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
            transpose_angle(bottom_left, 3, 3),
            transpose_angle(top_left, 3, -3),
            transpose_angle(bottom_right, -3, 3),
            transpose_angle(top_right, -3, -3),
        ]

        for void_zones, fill_zones in zip(voids, fills):
            for v_zone, f_zone in zip(void_zones, fill_zones):
                print(f"TRYING: {v_zone}, {f_zone}")
                f = lambda: mc.set_zone(v_zone, "air")
                await self.publish("mc.lambda", dumps(f))
                f = lambda: mc.set_zone(f_zone, "black_concrete")
                await self.publish("mc.lambda", dumps(f))

        # lights
        light_pos1 = pos1.offset(z=3 + extra_margin)
        light_pos2 = pos2.offset(z=3 + extra_margin)
        zone = mc.BlockZone(light_pos1, light_pos2)
        f = lambda: mc.set_zone(zone, "light")
        await self.call("mc.lambda", dumps(f))

        self.backboard_origin = origin

    async def remove_backboard(self):
        base_origin = self.config.paint_start
        extra_margin = self.config.backboard_extra_size

        print("-> Remove backboard")
        origin = base_origin.offset(z=-2)
        pos1 = origin.offset(x=-8 - extra_margin, y=-3 - extra_margin)
        pos2 = origin.offset(
            x=self.config.width + 8 + extra_margin,
            y=self.config.height + 3 + extra_margin,
        )

        zone = mc.BlockZone(pos1, pos2)
        f = lambda: mc.set_zone(zone, "air")
        await self.publish("mc.lambda", dumps(f))

        light_pos1 = pos1.offset(z=3 + extra_margin)
        light_pos2 = pos2.offset(z=3 + extra_margin)

        zone = mc.BlockZone(light_pos1, light_pos2)
        f = lambda: mc.set_zone(zone, "air")
        await self.publish("mc.lambda", dumps(f))

    async def remove_zone(self):
        pos1 = self.config.paint_start
        pos2 = pos1.offset(x=self.config.width, y=self.config.height, z=0)
        zone = mc.BlockZone(pos1, pos2)

        f = lambda: mc.set_zone(zone, "air")
        await self.publish("mc.lambda", dumps(f))

    async def compute_svg(self, filename):
        self.is_computing = True
        start = time.time()
        computing_config = {k: v for k, v in self.config.compute_data.items() if v is not None}

        print("\n" + ("-" * 10) + f"  Computing [{filename}]  " + ("-" * 10) + "\n")
        print(f"Config: {computing_config}\n")
        self.computed_svg = svg_to_block_lists(filename, palette=None, **computing_config)
        print(
            "\n"
            + ("-" * 10)
            + f"  Finished in [{time.time() - start:.0f}s]  "
            + ("-" * 10)
            + "\n"
        )

        await self.publish("painter.svg_ready")
        self.is_computing = False

    async def paint(self, word=None):
        
        if not self.computed_svg:
            print("-> No computed svg paint returned")
            return
        
        print("\n" + ("-" * 10) + f"  Painting [{word}]  " + ("-" * 10) + "\n")
        self.is_painting = True
        self.stop_painting = False
        
        ################################################
        
        block_list = self.computed_svg["block_list"]
        flattened_block_list = sum(block_list, [])
        print(f"-> Flattened {len(block_list)} layers into {len(flattened_block_list)} block list")
        
        ################################################
        
        n = max(1, self.config.paint_chunk_size)
        chunks = [
            flattened_block_list[i : i + n]
            for i in range(0, len(flattened_block_list), n)
        ]
        print(f"-> Computed {len(chunks)} chunks of {n} blocks each")
        
        ################################################
        
        interval, wait_time, steps = await self.get_interval(len(chunks))
        print(
            f"-> Will attempt in: {wait_time}: ({steps / (1000 / self.config.paint_chunk_size)}s to build) + ({steps} steps x {interval:.2f} = {steps*interval}s)"
        )
        
        ################################################
        
        start = time.time()
        start_pos = self.config.paint_start
        height = self.config.height

        def paint_chunk(height, start_pos, pixel_list):
            for p in pixel_list:
                pos = start_pos.offset(x=p["x"], y=height - p["y"])
                mc.set_block(pos, p["block"])
        
        print(
            f"-> Painting '{word}' [{len(flattened_block_list)} blocks] Estimated: {wait_time:.0f}s"
        )
        for n, chunk in enumerate(chunks):

            if not self.rush_paint and not self.fast_mode:
                await asyncio.sleep(interval)

            print(f"-> Painting chunk [{n+1}/{len(chunks)}]" + (' - [FAST] ' if (self.rush_paint or self.fast_mode) else ''), end="\r")
            
            f = lambda: paint_chunk(height, start_pos, chunk)
            await self.publish("mc.lambda", dumps(f))

            if self.stop_painting:
                print("\n-> Was ordered to stop painting")
                break

        self.rush_paint = False
        await self.publish("painter.finished")

        print(
            "\n"
            + ("-" * 10)
            + f"  Finished in [{time.time() - start:.0f} seconds]  "
            + ("-" * 10)
            + "\n"
        )
        
        self.is_painting = False


if __name__ == "__main__":
    action = Painter()
    asyncio.run(action.run())
