import asyncio
import shulker as mc
from dill import dumps

from tools.pulsar import Portal


class Podium(Portal):
    async def on_join(self):
        await self.subscribe("gl.spawn_winner", self.spawn_winner)
        await self.subscribe("gl.reset_podium", self.reset_podium)

    async def reset_podium(self):
        cmd = f"/npc remove all"
        await self.publish("mc.post", cmd)

    async def spawn_winner(self, pos, name, score):
        cmd = f'/npc create --at{pos[0]}:{pos[1]}:{pos[2]} --nameplate true "{name} Score: {score}"'
        await self.publish("mc.post", cmd)


if __name__ == "__main__":
    action = Podium()
    asyncio.run(action.run())
