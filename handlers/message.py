import asyncio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
import mcapi as mc
import random
import json
import re

config = {}
with open("config.json", "r") as f:
  config = json.load(f)

normal_queue = []
follower_queue = []
donator_queue = []
forced_queue = []

class Component(ApplicationSession):
    async def onJoin(self, details):
        
        # Each 'message' is a tuple of (pseudo, text, extra)
        def on_message(message):
            pseudo = message[0]
            text = message[1]
            extra = message[2]
            
            if pseudo and pseudo.lower().startswith('chec'):
              return
            
            forced = [".: Moderator :.", "Subscriber", "* TOP GIFTER *"]
            donator = ["~ New Gifter ~"]

            if extra and extra in forced:
              forced_queue.append(message)
              
            elif extra and extra == 'Follower':
              if len(follower_queue) > 3:
                del follower_queue[random.randint(0, len(follower_queue) - 1)]
              follower_queue.append(message)
            
            elif extra and extra in donator:
              if len(donator_queue) > 4:
                del donator_queue[random.randint(0, len(donator_queue) - 1)]
              donator_queue.append(message)
              
            else:
              if len(normal_queue) > 2:
                del normal_queue[random.randint(0, len(normal_queue) - 1)]
              normal_queue.append(message)

        await self.subscribe(on_message, 'chat.comment')
        
        async def next_message():
            
            if normal_queue or follower_queue or donator_queue:
              
              # First we print the length of all 3 queues
              print(f"normal: {len(normal_queue)}, follower: {len(follower_queue)}, donator: {len(donator_queue)} forced: {len(forced_queue)} total: {len(normal_queue) + len(follower_queue) + len(donator_queue) + len(forced_queue)}")

              # 80% chance to display a donator message
              # 15% chance to display a follower message
              # 5% chance to display a normal message
              
              # If there is no donator message, then 80% chance to display a follower message
              # and 20% chance to display a normal message
              
              # If there is no donator or follower message, then 100% chance to display a normal message
              
              def pick_from_queue():
                if forced_queue:
                  return forced_queue.pop(0)
                  
                elif donator_queue:
                  
                  randint = random.randint(0, 100)
                  
                  if 0 <= randint <= 80:
                    return donator_queue.pop(0)
                  elif 80 < randint <= 95:
                    return follower_queue.pop(0)
                  else:
                    try:
                      return normal_queue.pop(0)
                    except:
                      return None
                  
                elif follower_queue:
                  
                  randint = random.randint(0, 100)
                  
                  if 0 <= randint <= 60:
                    return follower_queue.pop(0)
                  else:
                    try:
                      return normal_queue.pop(0)
                    except:
                      return None
                  
                else:
                  if normal_queue:
                    try:
                      return normal_queue.pop(0)
                    except:
                      return None
                  else:
                    return None
                
              def decide_message_style(extra):
                if extra == '* TOP GIFTER *':
                  return 'top_gifter'
                elif extra == '~ New Gifter ~':
                  return 'new_gifter'
                else:
                  return 'default'
                
              msg = pick_from_queue()
              
              if msg:
                
                pseudo, text, extra = msg
                
                # Gets trollzered
                if text.lower() == "gay":
                  text = "I'm gay <3"

                # Shorten messages longer than 50 characters and end with '...'
                text = text[:50] + "..." if len(text) > 50 else text
                
                style = decide_message_style(extra)
                self.publish('printer.generate_text', style, text, pseudo, extra)
                
            await asyncio.sleep(2.5)
            asyncio.get_event_loop().create_task(next_message())
            
        await next_message()    

    def onDisconnect(self):
        asyncio.get_event_loop().stop()


if __name__ == '__main__':
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(Component)