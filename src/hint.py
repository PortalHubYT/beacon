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
        pos1 = config.hint_start.offset(x=-config.width, y=-5)
        pos2 = config.hint_start.offset(x=config.width, y=5)
        zone = mc.BlockZone(pos1, pos2)

        f = lambda: mc.set_zone(zone, "air")
        await self.publish("mc.lambda", dumps(f))

    async def print_hint(self, hint):
        print("-> Printing hint :", hint)

        def print_hint_get_zone():
            hint_pos = config.hint_start
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
        await self.publish("mc.lambda", dumps(f))


if __name__ == "__main__":
    action = Hint()
    asyncio.run(action.run())
