import asyncio
import shulker as mc
from dill import dumps

from tools.pulsar import Portal
from tools.database import db

queue = []

class Join(Portal):
    async def on_join(self):
        
        async def on_live_join(profile):
            
            viewers = db.get("SELECT count FROM views ORDER BY timestamp DESC LIMIT 1", one=True)
            if viewers is None or viewers[0] > 50: return
            
            queue.append(profile)
        
        await self.subscribe('live.join', on_live_join)
    
    async def loop(self):
        
        if queue:
            profile = queue.pop(0)
            print(f"-> join queue len: {len(queue)}")
            
            profile["comment"] = "&ko&r Joined the live! &ko&r"
            
            await self.publish('live.comment', profile)
            
        await asyncio.sleep(0.1)
        
if __name__ == "__main__":
    action = Join()
    asyncio.run(action.run())