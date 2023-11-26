import asyncio
import uuid

import shulker as mc
from dill import dumps

from tools.pulsar import Portal


class Guesses(Portal):
    async def on_join(self):
        
        await self.subscribe("live.comment", self.on_comment)
        self.chat_queue = []
        self.colors = ["light_purple", "aqua", "dark_green", "green", "yellow", "red", "dark_red", "dark_purple"]
        self.color_index = 0
        self.coords = mc.Coordinates(5, 60, 17)

        await self.loop()
        
    async def on_comment(self, user):
        if len(user["display"]) > 14:
            user["display"] = user["display"][:14] + "..."
        if len(user["comment"]) > 14:
            user["comment"] = user["comment"][:14] + "..."
        
        if '"' in user["display"] or "'" in user["display"] or '"' in user["comment"] or "'" in user["comment"]:
            return
        
        self.chat_queue.insert(0, user)
        if len(self.chat_queue) > 5:
            self.chat_queue = self.chat_queue[-1:]
    
    async def loop(self):
        if self.chat_queue:
            
            next_user = self.chat_queue.pop(0)
            name = next_user["display"]
            comment = next_user["comment"]
            
            unique_tag = uuid.uuid4()
            
            cmd = """summon text_display $coords {teleport_duration:10000,alignment:"left",Tags:["chat_guess", "$unique_tag"],text:'[{"text":"$display","color":"$color","bold":true,"underlined":true},{"text":"\n$guess","color":"white","bold":false,"underlined":false}]'}"""
            cmd = cmd.replace("$display", f"{name}:")
            cmd = cmd.replace("$guess", f"{comment}")
            cmd = cmd.replace("$coords", f"{self.coords}")
            cmd = cmd.replace("$color", f"{self.colors[self.color_index]}")
            cmd = cmd.replace("$background", f"{0}")
            cmd = cmd.replace("$unique_tag", f"{unique_tag}")

            print(cmd)
            await self.publish("mc.post", cmd)
            
            tp_cmd = f"execute as @e[tag={unique_tag}] at @s run tp @s ~ ~22 ~"
            await self.publish("mc.post", tp_cmd)
            
            self.color_index += 1
            if self.color_index >= len(self.colors):
                self.color_index = 0
        
        await asyncio.sleep(0.1)
    
        
if __name__ == "__main__":
    action = Guesses()
    asyncio.run(action.run())

