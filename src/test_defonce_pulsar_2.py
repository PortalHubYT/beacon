import asyncio
import shulker as mc
from dill import dumps

from tools.pulsar import Portal

class Template(Portal):
    async def on_join(self):
        await self.subscribe("mcpopo", self.popo)

    async def popo(self, user):
        print(user)
        
if __name__ == "__main__":
    action = Template()
    asyncio.run(action.run())

