import asyncio

import shulker as mc
from dill import dumps

from tools.pulsar import Portal


class Template(Portal):
    async def on_join(self):
        
        f = lambda: mc.say('hello')
        await self.publish('mc.lambda', dumps(f))
        
        cmd = "say world!"
        ret = await self.call('mc.post', cmd)
        print(ret) # Will be an empty string, say commands have no return
        
if __name__ == "__main__":
    action = Template()
    asyncio.run(action.run())

