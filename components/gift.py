import asyncio
import random
import os
import sys
import json

import shulker as mc

from tools.sanitize import pick_display, crop, sanitize
from tools.odds import pick_from_queue, flip_coin

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from dill import dumps

with open("config.json", "r") as f:
    config = json.load(f)

queue = []


class Component(ApplicationSession):
    async def onJoin(self, details):
        async def on_gift(profile):
            """Uncomment this if you want half of the joins to be ignored
            if flip_coin(): return"""

            name = pick_display(profile)
            if not name:
                return

            gift = profile["gift"]

            print(f"-> gift queue len: {len(queue)}")
            queue.append([name, gift])

        async def next_gift():
            if queue:
                name, gift = queue.pop(0)
                print(f"[{name}] gifted: {gift}")
                # do stuff
                pass

            await asyncio.sleep(0.1)
            asyncio.get_event_loop().create_task(next_gift())

        await self.subscribe(on_gift, "chat.gift")
        await next_gift()


if __name__ == "__main__":
    print("Starting Gift Handler...")
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(Component)
