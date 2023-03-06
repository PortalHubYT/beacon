import asyncio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
import re
import random

queue = []

class Component(ApplicationSession):
    
    async def onJoin(self, details):
        
        self.follows = 0
        async def on_follow(name):
          
            pile_ou_face = random.randint(0, 2)
            if pile_ou_face != 0:
              return
            
            try:
                name = re.sub('[^A-Za-z0-9]+', '', name)
            except:
                pass
            print(f"follow queue len: {len(queue)}")
            queue.append(name)
            
        async def next_follow():
            if queue:
                name = queue.pop(0)
            else:
                name = None
            
            if name:
                rand_x = random.randint(-3, 3)
                rand_y = random.randint(-2, 2)
                cmd = f"execute at Miaoumix run summon chicken ~{rand_x} ~{rand_y} ~-40 {{CustomNameVisible:1b, Motion:[0.0,0.0,-1.0], CustomName:'{{\"text\":\"{name} followed!\"}}', ActiveEffects:[{{Id:28b,Amplifier:5b,Duration:20000}}]}}"
                self.follows += 1
                self.call("minecraft.post", cmd)
            
            await asyncio.sleep(0.1)
            asyncio.get_event_loop().create_task(next_follow())
            
        await self.subscribe(on_follow, 'chat.follow')
        await next_follow()
        
        
                
if __name__ == '__main__':
    
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(Component)