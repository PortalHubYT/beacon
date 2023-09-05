import asyncio
import random

import shulker as mc
from dill import dumps

from tools.config import config
from tools.pulsar import Portal


class Hint(Portal):
    async def on_join(self):
        await self.subscribe("gl.print_hint", self.print_hint)
        await self.subscribe("gl.clear_hint", self.clear_hint)

        # in case we cut this process and something remains
        cmd = f"sudo {config.camera_name} //replacenear 100 blackstone,blackstone_slab,blackstone_stairs,blackstone_wall air"
        await self.publish("mc.post", cmd)

    async def clear_hint(self):
        if hasattr(self, "hint_zone"):
            print("-> Clearing hint zone")
            await self.publish("mc.post", f"fill {self.hint_zone} air")
        else:
            print("-> No hint zone to clear")

    async def print_hint(self, hint):
        def print_hint_get_zone():
            hint_pos = mc.BlockCoordinates(
                config.camera_pos.x,
                config.camera_pos.y + config.hint_height,
                config.camera_pos.z - config.hint_distance,
            )

            status = mc.meta_set_text(
                hint,
                mc.BlockCoordinates(0, 0, 0),
                ["quartz"],
                "mixed",
                "east",
                mc.BlockHandler("replace"),
                0,
                mc.Block("air"),
                "minecraft",
            )
            zone = status["zone"]
            hint_pos = hint_pos.offset(x=-((zone.pos2.x - zone.pos1.x) / 2))

            status = mc.set_text(hint, hint_pos)
            return status["zone"]

        f = lambda: print_hint_get_zone()
        zone = await self.call("mc.lambda", dumps(f))

        zone_tuples = zone.split(" ")
        corner_1_coords = zone_tuples[: len(zone_tuples) // 2]
        corner_1 = mc.BlockCoordinates(*corner_1_coords)
        corner_2_coords = zone_tuples[len(zone_tuples) // 2 :]
        corner_2 = mc.BlockCoordinates(*corner_2_coords)
        self.hint_zone = mc.BlockZone(corner_1, corner_2)


if __name__ == "__main__":
    action = Hint()
    asyncio.run(action.run())
