import asyncio
from tools._base_action import BaseAction

class Join(BaseAction):
    async def on_join(self):
        
        async def say_hello(profile):
            ret = await self.call('mc.post', f"say Hello ddt{profile['display']}!")
            print(f"-> {ret}")
         
        await say_hello({'display': 'test'})   
        #await self.subscribe('live.join', say_hello)
        
if __name__ == "__main__":
    action = Join()
    asyncio.run(action.run())

