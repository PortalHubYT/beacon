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

# Work around to be able to import from the same level folder 'tools'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import config, db

queue = []


class Component(ApplicationSession):
    async def onJoin(self, details):
        self.likes = 0

        async def on_like(profile):
            """Uncomment this if you want half of the joins to be ignored
            if flip_coin(): return"""

            name = pick_display(profile)
            if not name:
                return

            print(f"-> like queue len: {len(queue)}")
            queue.append(name)

        async def next_like():
            if queue:
                name = queue.pop(0)
                print(f"[{name}] liked")
                # do stuff
                pass

            await asyncio.sleep(0.1)
            asyncio.get_event_loop().create_task(next_like())

        await self.subscribe(on_like, "chat.like")
        await next_like()


if __name__ == "__main__":
    print("Starting Like Handler...")
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(Component)
