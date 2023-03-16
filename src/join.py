import asyncio
import shulker as mc
from dill import dumps

from tools._base_action import BaseAction

class Join(BaseAction):
    async def on_join(self):
        
        async def say_hello(profile):
            f = lambda: mc.say('test')
            
            ret = await self.publish('mc.lambda', dumps(f))
            print(f"-> Game returned: {ret}")
         
        await say_hello({'display': 'test'})   
        #await self.subscribe('live.join', say_hello)
        
if __name__ == "__main__":
    action = Join()
    asyncio.run(action.run())

