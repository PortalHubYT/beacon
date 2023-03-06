import asyncio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from random import randint

queue = []
  
class Component(ApplicationSession):
    
    async def onJoin(self, details):
        
        """# Streakable gift & streak is over
          if event.gift.streakable and not event.gift.streaking:
              pass"""
        
        async def gift_handler(event):
          pass
        
        async def on_gift_streak():
          
          pass
          
        async def on_gift(gift):
            
          pass
        
        await self.subscribe(gift_handler, 'chat.gift')
        
        
                
if __name__ == '__main__':
    print("Starting Gift Handler...")
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(Component)