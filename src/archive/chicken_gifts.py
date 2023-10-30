import asyncio
import importlib

import shulker as mc
from dill import dumps

import tools.config
from tools.pulsar import Portal


class Gift(Portal):
    async def on_join(self):
        
        await self.reload_config()

        await self.subscribe("live.gift", self.on_gift)
        await self.subscribe("gl.reload_config", self.reload_config)

        self.queue = []

        cmd = f'summon text_display -2.1 69 23 {{billboard:"center", text:\'{{"text":"Gifters ↑","color":"gold"}}\',background:-16777216}}'
        await self.publish("mc.post", cmd)
        await self.loop()

    async def reload_config(self):
        importlib.reload(tools.config)
        self.config = tools.config.config

    async def on_gift(self, user):
        print("gift", user["display"])
        cmd = f'summon chicken -4.2 85 18.5 {{InLove:20000,NoGravity:0b,CustomNameVisible:1b,Age:-20000,CustomName:\'{{"text":"{user["display"][:15]}"}}\',active_effects:[{{id:"minecraft:slow_falling",amplifier:10b,duration:20000}}]}}'
        print(cmd)
        self.queue.append(cmd)

    async def loop(self):
        while True:
            if len(self.queue) > 0:
                cmd = self.queue.pop(0)
                await self.publish("mc.post", cmd)
            await asyncio.sleep(0.8)


if __name__ == "__main__":
    action = Gift()
    asyncio.run(action.run())
