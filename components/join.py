import asyncio
import random
import os
import sys
import json

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from dill import dumps
import shulker as mc

from tools.sanitize import pick_display, crop, sanitize
from tools.odds import pick_from_queue, flip_coin
from ..config import config, db, pulsar, prefix

queue = []


class Component(ApplicationSession):
    async def onJoin(self, details):
        async def on_join(profile):
            """Uncomment this if you want half of the joins to be ignored
            if flip_coin(): return"""

            name = pick_display(profile)
            if not name:
                return

            print(f"-> join queue len: {len(queue)}")
            queue.append(name)

        async def next_join():
            if queue:
                name = queue.pop(0)
                # do stuff
                pass

            await asyncio.sleep(0.01)
            asyncio.get_event_loop().create_task(next_join())

        await self.subscribe(on_join, "chat.join")
        await next_join()


if __name__ == "__main__":
    print("Starting Join Handler...")
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(Component)
