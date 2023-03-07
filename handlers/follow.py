import asyncio
import os
import sys

import shulker as mc

# Work around to be able to import from the same level folder 'tools'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.sanitize import pick_display
from tools.odds import flip_coin

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from dill import dumps

queue = []

class Component(ApplicationSession):
    
    async def onJoin(self, details):
        
        async def on_follow(profile):
          
            """ Uncomment this if you want half of the follows to be ignored
            if flip_coin():
              return"""
            
            name = pick_display(profile)
            if not name: return
            
            print(f"-> follow queue len: {len(queue)}")
            queue.append(name)
            
        async def next_follow():
          
            if queue:
                name = queue.pop(0)
                # do stuff
                pass
            
            await asyncio.sleep(0.1)
            asyncio.get_event_loop().create_task(next_follow())
            
        await self.subscribe(on_follow, 'chat.follow')
        await next_follow()
        
        
                
if __name__ == '__main__':
    print("Starting Follow Handler...")
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(Component)