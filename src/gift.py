import asyncio
import shulker as mc
from dill import dumps
import importlib

from tools.pulsar import Portal
import tools.config


class Gift(Portal):
    async def on_join(self):
        await self.reload_config()

        await self.subscribe("gift.build_pipe", self.build_pipe)
        await self.subscribe("live.gift", self.on_gift)
        await self.subscribe("gl.reload_config", self.reload_config)

        # await self.build_pipe()

    async def reload_config(self):
        importlib.reload(tools.config)
        self.config = tools.config.config

    async def on_gift(self, user):
        print("gift", user["display"])
        pos = self.config["podium_pos"].offset(x=-6, y=9, z=-11)

        cmd = f"summon chicken {pos} {{NoGravity:0b,Glowing:1b,CustomNameVisible:1b,CustomName:'{{\"text\":\"Gift by {user['display'][:15]}\"}}',ActiveEffects:[{{Id:28,Amplifier:5b,Duration:20000,ShowParticles:0b}}]}}"
        await self.publish("mc.post", cmd)

    async def build_pipe(self):
        pos1 = self.config["podium_pos"].offset(x=-5, y=-6, z=-10)
        pos2 = pos1.offset(x=-2, y=20, z=-2)

        zone = mc.BlockZone(pos1, pos2)
        f = lambda: mc.set_zone(zone, "barrier")
        await self.publish("mc.lambda", dumps(f))

        hole_pos1 = pos1.offset(x=-1, y=0, z=-1)
        hole_pos2 = pos2.offset(x=1, y=0, z=1)
        hole_zone = mc.BlockZone(hole_pos1, hole_pos2)
        f = lambda: mc.set_zone(hole_zone, "air")
        await self.publish("mc.lambda", dumps(f))


if __name__ == "__main__":
    action = Gift()
    asyncio.run(action.run())
