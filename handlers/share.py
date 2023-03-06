import asyncio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
import re
import random

queue = []

class Component(ApplicationSession):
    
    async def onJoin(self, details):
        
        self.shares = 0
        async def on_share(name):
            try:
                name = re.sub('[^A-Za-z0-9]+', '', name)
            except:
                pass
            print(f"share queue len: {len(queue)}")
            queue.append(name)
            
        async def next_share():
            if queue:
                name = queue.pop(0)
            else:
                name = None
            
            if name:
                rand_x = random.randint(-7, 7)
                rand_y = random.randint(-2, 2) - 15
                cmd = f'title Miaoumix actionbar {{"text":"Thanks for sharing {name}, slime for you!"}}'
                self.call("minecraft.post", cmd)
                cmd = f"execute at Miaoumix run summon slime ~{rand_x} ~{rand_y} ~-80 {{CustomNameVisible:1b, Size:5, CustomName:'{{\"text\":\"{name}\"}}', Motion:[0.0,0.0,-1.0], ActiveEffects:[{{Id:28b,Amplifier:5b,Duration:20000}}]}}"
                self.shares += 1
                self.call("minecraft.post", cmd)
            
            await asyncio.sleep(0.1)
            asyncio.get_event_loop().create_task(next_share())
            
        await self.subscribe(on_share, 'chat.share')
        await next_share()
        
        
                
if __name__ == '__main__':
    print("Starting Share Handler...")
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(Component)