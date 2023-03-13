import asyncio
import random
import os
import sys

import shulker as mc
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

from tools.sanitize import pick_display, crop, sanitize
from tools.odds import pick_from_queue, flip_coin
from config import config, db

queue = []

class Component(ApplicationSession):
    async def onJoin(self, details):
      
        # One way to use Shulker is to lambda the function
        # Serialize it and use the poster to execute it
        # This allows you to use the Shulker decorating functions
        f = lambda: mc.say("Hello")
        self.publish("mc.lambda", dumps(f))

        # Another one would be to call the meta functions of Shulker
        # And send the instructions to the poster and it'll post it
        # This only allows you to use the Shulker functions that return the bare command
        cmd = mc.meta_say("World!")
        self.publish("mc.post", cmd)

        # If you need return values from the Shulker functions
        # use self.call('mc.lambda', dumps(f))
        # or self.call('mc.post', cmd)
        f = lambda: mc.get_player_pos("Miaoumix", rounded=False)
        pos = await self.call("mc.lambda", dumps(f))

        f = lambda: mc.say(f"Your position: {pos}")
        self.publish("mc.lambda", dumps(f))

        async def start():
            pass

        await self.subscribe(start, "template_component.start")


if __name__ == "__main__":
    print("Starting Template Component...")
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(Component)
