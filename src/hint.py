import asyncio
import random
import time
import importlib

import shulker as mc
from dill import dumps

import tools.config
from tools.pulsar import Portal


class Hint(Portal):
    async def on_join(self):
        await self.reload_config()

        self.hint = None

        await self.subscribe("hint.print", self.print_hint)
        await self.subscribe("hint.clear", self.clear_hint)
        await self.subscribe("hint.reload", self.reload_hint)
        await self.subscribe("gl.reload_config", self.reload_config)

    async def reload_config(self):
        importlib.reload(tools.config)
        self.config = tools.config.config

    async def reload_hint(self, hint):
        await self.clear_hint()
        await self.reload_config()
        await self.print_hint(hint)

    async def clear_hint(self):
        pos1 = self.config.hint_start.offset(x=-self.config.width, y=-5)
        pos2 = self.config.hint_start.offset(x=self.config.width, y=5)
        zone = mc.BlockZone(pos1, pos2)

        f = lambda: mc.set_zone(zone, "air")
        await self.publish("mc.lambda", dumps(f))

    async def print_hint(self, hint):
        hint = hint.upper()
        print("-> Printing hint :", hint)

        self.hint = hint

        def print_hint_get_zone(hint_pos, hint_palette):
            status = mc.meta_set_text(
                hint,
                mc.BlockCoordinates(0, 0, 0),
                [hint_palette],
                "mixed",
                "east",
                mc.BlockHandler("replace"),
                0,
                mc.Block("air"),
                "minecraft",
            )
            zone = status["zone"]
            hint_pos = hint_pos.offset(x=-((zone.pos2.x - zone.pos1.x) / 2))

            mc.set_text(hint, hint_pos, palette=[hint_palette])

        hint_pos = self.config.hint_start
        hint_palette = self.config.hint_palette
        f = lambda: print_hint_get_zone(hint_pos, hint_palette)
        await self.publish("mc.lambda", dumps(f))


if __name__ == "__main__":
    action = Hint()
    while True:
        try:
            asyncio.run(action.run(), debug=True)
        except Exception as e:
            error_msg = f"An error occurred: {e}"
            print(error_msg)
            print("-> Restarting in 1 seconds...")
            time.sleep(1)
