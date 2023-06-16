import asyncio
import random

import shulker as mc
from dill import dumps

from tools.pulsar import Portal
from tools.sanitize import crop, sanitize
from tools.odds import pick_from_queue
from tools.config import config

empty_queue = []
normal_queue = []
follower_queue = []
priority_queue = []
bypass_queue = []

class Comment(Portal):
    async def on_join(self):
        
        def on_message(profile):

            role = profile["role"]
            
            bypass = ["Moderator", "Subscriber", "Top Gifter"]
            priority = ["New Gifter"]

            total = len(normal_queue) + len(follower_queue) + len(priority_queue) + len(bypass_queue)
            
            if "Joined the live!" in profile["comment"] and total == 0:
              if len(empty_queue) > 2:
                del empty_queue[random.randint(0, len(empty_queue) - 1)]
              empty_queue.append(profile)
              
            elif "Joined the live!" not in profile["comment"]:
              
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
              
            print(f"--ADDING--> normal: {len(normal_queue)}, follower: {len(follower_queue)}, donator: {len(priority_queue)} forced: {len(bypass_queue)} total: {total}")

        await self.subscribe('live.comment', on_message)
    
    async def loop(self):
        
        total = len(normal_queue) + len(follower_queue) + len(priority_queue) + len(bypass_queue)
        
        if total > 0:
                    
            queues = [normal_queue, follower_queue, priority_queue, bypass_queue]
            profile = pick_from_queue(queues)
            print(f"-POPPING--> normal: {len(normal_queue)}, follower: {len(follower_queue)}, donator: {len(priority_queue)} forced: {len(bypass_queue)} total: {total}")
            if not profile: return
            
            display = ""
            
            if profile["role"]:
                colors = ["1", "2", "3", "4", "5", '6', '7', '8', '9', '0', 'a', 'b', 'c', 'd', 'e', 'f']
                display += "&" + random.choice(colors) + "&l"
            else:
                display += "&l"
            
            def spawn_npc(name, message, display):
                
                origin = config.npc_spawn_pos
                
                x_offset = random.randint(-2, 2)
                z_offset = random.randint(-2, 2)
                
                shifted = origin.offset(x_offset, 30, z_offset)
                
                spawn_pos = str(shifted).replace(" ", ":")
                
                ret = mc.post(f"npc create {display}{name} --at {spawn_pos}:world")
                
                mc.post(f"effect give @e minecraft:slow_falling infinite 1 true")
                
                ret = ret.replace("\x1b[0m", "").replace("\x1b[32;1m", "").replace("\x1b[33;1m", "").replace("\n", "")
                id = ret.split("ID ")[1].replace(").", "")

                val1 = int(id)
                val2 = int(config.cleanup_threshold)
                if val1 % val2 == 0:
                    mc.post(f'execute as {config.camera_name} at @e[name=!PortalHub,name=!{config.camera_name}] run particle minecraft:poof ~ ~ ~ 0.7 1 0.7 0.01 500')
                    mc.post(f'npc remove all')
                
                mc.post(f"npc vulnerable --id {id}")
                mc.post(f"npc health --set 1 --id {id}")
                mc.post(f"npc speed 0.7 --id {id}")
                mc.post(f"npc scoreboard --addtag alive")
                

            comment = comment.replace("/", "")
            f = lambda: spawn_npc(profile['display'], comment, display)
            await self.publish('mc.lambda', dumps(f))
                
        await asyncio.sleep(1.5)
        
if __name__ == "__main__":
    action = Comment()
    asyncio.run(action.run())
