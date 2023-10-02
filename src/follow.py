import asyncio
import importlib

import shulker as mc
from dill import dumps

import tools.config
from tools.pulsar import Portal


class Follow(Portal):
    async def on_join(self):
        
        await self.reload_config()

        await self.subscribe("follow.build_pipe", self.build_pipe)
        await self.subscribe("live.follow", self.on_follow)
        await self.subscribe("gl.reload_config", self.reload_config)

        self.queue = []

        cmd = f'summon text_display 3.11 69 23 {{billboard:"center", text:\'{{"text":"Follow ↑","color":"gold"}}\',background:-16777216}}'
        await self.publish("mc.post", cmd)
        await self.loop()

    async def reload_config(self):
        importlib.reload(tools.config)
        self.config = tools.config.config

    async def on_follow(self, user):
        print("follow", user["display"])
        cmd = f'summon villager 5.1 67 18.5 {{NoGravity:0b,CustomNameVisible:1b,Age:-20000,CustomName:\'{{"text":"{user["display"][:15]}"}}\',ActiveEffects:[{{Id:25,Amplifier:1b,Duration:20000,ShowParticles:0b}}]}}'
        self.queue.append(cmd)

    async def build_pipe(self):
        pos1 = self.config["podium_pos"].offset(x=7, y=-6, z=-10)
        pos2 = pos1.offset(x=-2, y=20, z=-2)

        zone = mc.BlockZone(pos1, pos2)
        f = lambda: mc.set_zone(zone, "barrier")
        await self.publish("mc.lambda", dumps(f))

        hole_pos1 = pos1.offset(x=-1, y=0, z=-1)
        hole_pos2 = pos2.offset(x=1, y=0, z=1)
        hole_zone = mc.BlockZone(hole_pos1, hole_pos2)
        f = lambda: mc.set_zone(hole_zone, "air")
        await self.publish("mc.lambda", dumps(f))


    async def loop(self):
        while True:
            if len(self.queue) > 0:
                cmd = self.queue.pop(0)
                await self.publish("mc.post", cmd)
            await asyncio.sleep(0.8)


if __name__ == "__main__":
    action = Follow()
    asyncio.run(action.run())
