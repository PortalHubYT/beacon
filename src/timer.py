import asyncio
import time
import importlib
import shulker as mc
from dill import dumps

import tools.config
from tools.pulsar import Portal


class Timer(Portal):
    async def on_join(self):
        
        await self.reload_config()
        
        await self.subscribe("gl.reload_config", self.reload_config)
        await self.subscribe("gl.timer", self.initialize_timer)
        await self.subscribe("gl.set_timer", self.set_timer)
        await self.initialize_timer()

    async def reload_config(self):
        importlib.reload(tools.config)
        self.config = tools.config.config
        
    async def initialize_timer(self):
        print("-> Initializing timer")
        f = lambda: mc.remove_bossbar("timer")
        await self.publish("mc.lambda", dumps(f))

        round_time = self.config.round_time
        f = lambda: mc.create_bossbar(
            "timer",
            "Guess the word in chat!",
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
        print("-> Setting timer to", value)
        f = lambda: mc.set_bossbar("timer", "value", value)
        ret = await self.publish("mc.lambda", dumps(f))


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
