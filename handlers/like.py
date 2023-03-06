import asyncio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
import re
import random

queue = []

class Component(ApplicationSession):
    
    async def onJoin(self, details):
        
        self.likes = 0
        async def on_like(name):
            try:
                name = re.sub('[^A-Za-z0-9]+', '', name)
            except:
                pass
            print(f"like queue len: {len(queue)}")
            queue.append(name)
            
        async def next_like():
            if queue:
                name = queue.pop(0)
            else:
                name = None
            
            if name:
                rand_x = random.randint(-7, 7)
                rand_y = random.randint(-2, 2) + 5
                cmd = f"execute at Miaoumix run summon slime ~{rand_x} ~{rand_y} ~-40 {{CustomNameVisible:1b, Size:0, Motion:[0.0,0.0,-1.0], CustomName:'{{\"text\":\"{name} liked\"}}', ActiveEffects:[{{Id:28b,Amplifier:5b,Duration:20000}}]}}"
                self.likes += 1
                self.call("minecraft.post", cmd)
            
            
            await asyncio.sleep(0.1)
            asyncio.get_event_loop().create_task(next_like())
            
        await self.subscribe(on_like, 'chat.like')
        await next_like()
        
        
                
if __name__ == '__main__':
    
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(Component)