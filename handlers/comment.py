import asyncio
import random

import shulker as mc
from tools.sanitizer import sanitize, crop
from tools.odds import pick_from_queue

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

normal_queue = []
follower_queue = []
priority_queue = []
bypass_queue = []

class Component(ApplicationSession):
    async def onJoin(self, details):
        
        # Each 'message' is a tuple of (pseudo, text, extra)
        def on_message(profile):

            if not profile["comment"]:
              print(f"No comment to parse")
              return
            else:
              profile["comment"] = sanitize(profile["comment"])
              profile["nickname"] = sanitize(profile["nickname"])
              if profile["nickname"] == "":
                profile["nickname"] = profile["unique_id"]
              role = profile["role"]
            
            bypass = ["Moderator", "Subscriber", "Top Gifter"]
            priority = ["New Gifter"]

            if role in bypass:
              bypass_queue.append(profile)
              
            elif role == "Follower":
              if len(follower_queue) > 3:
                del follower_queue[random.randint(0, len(follower_queue) - 1)]
              follower_queue.append(profile)
            
            elif role in priority:
              if len(priority_queue) > 4:
                del priority_queue[random.randint(0, len(priority_queue) - 1)]
              priority_queue.append(profile)
              
            else:
              if len(normal_queue) > 2:
                del normal_queue[random.randint(0, len(normal_queue) - 1)]
              normal_queue.append(profile)

        await self.subscribe(on_message, 'chat.comment')
        
        async def next_message():
            
            if normal_queue or follower_queue or priority_queue:
              
              print(f"normal: {len(normal_queue)}, follower: {len(follower_queue)}, donator: {len(priority_queue)} forced: {len(bypass_queue)} total: {len(normal_queue) + len(follower_queue) + len(priority_queue) + len(bypass_queue)}")
              
              queues = [normal_queue, follower_queue, priority_queue, bypass_queue]
              profile = pick_from_queue(queues)
              
              if profile:

                text = crop(profile["comment"])
                name = crop(profile["nickname"])
                pass
                
            await asyncio.sleep(2.5)
            asyncio.get_event_loop().create_task(next_message())
            
        await next_message()    

    def onDisconnect(self):
        asyncio.get_event_loop().stop()


if __name__ == '__main__':
    print("Starting Comment Handler...")
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(Component)