import asyncio
import shulker as mc
from dill import dumps

from tools.config import config
from tools.pulsar import Portal


class Timer(Portal):
    async def on_join(self):
        await self.subscribe("gl.timer", self.initialize_timer)
        await self.subscribe("gl.set_timer", self.set_timer)
        await self.initialize_timer()

    async def initialize_timer(self):
        print("-> Initializing timer")
        f = lambda: mc.remove_bossbar("timer")
        await self.publish("mc.lambda", dumps(f))

        round_time = config.round_time
        f = lambda: mc.create_bossbar(
            "timer",
            "Guess the word",
            value=round_time,
            color="red",
            style="progress",
            max=100,
            visible=True,
        )
        await self.publish("mc.lambda", dumps(f))

    async def set_timer(self, value):
        """
        value: int between 0 and 100
        """
        f = lambda: mc.set_bossbar("timer", "value", value)
        ret = await self.publish("mc.lambda", dumps(f))


if __name__ == "__main__":
    action = Timer()
    asyncio.run(action.run())
