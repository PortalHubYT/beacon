import asyncio

import shulker as mc
from dill import dumps

from tools.pulsar import Portal


class Guesses(Portal):
    async def on_join(self):
        
        await self.subscribe("live.comment", self.on_comment)
        self.chat_queue = []
        self.colors = ["light_purple", "aqua", "dark_green", "green", "yellow", "red", "dark_red", "dark_purple"]
        self.color_index = 0
        self.coords = mc.Coordinates(-6, 69, 23)

        cmds = [
            """setblock 7 70 22 minecraft:repeating_command_block[conditional=false,facing=up]{Command:"/kill @e[type=minecraft:text_display, distance=0..2]",CustomName:'{"text":"@"}',LastExecution:1992554L,SuccessCount:0,TrackOutput:0b,UpdateLastExecution:1b,auto:1b,conditionMet:1b,powered:1b}""",
            """setblock 8 70 22 minecraft:repeating_command_block[conditional=false,facing=south]{Command:"/kill @e[type=minecraft:chicken, distance=0..2]",CustomName:'{"text":"@"}',LastExecution:1986171L,SuccessCount:0,TrackOutput:0b,UpdateLastExecution:1b,auto:1b,conditionMet:1b,powered:1b}""",
            """setblock 9 70 22 minecraft:repeating_command_block[conditional=false,facing=south]{Command:"execute as @e[type=chicken] at @s run tp ~0.1 ~ ~",CustomName:'{"text":"@"}',LastExecution:1992910L,SuccessCount:140,TrackOutput:0b,UpdateLastExecution:1b,auto:1b,conditionMet:1b,powered:1b}""",
            ]
        for cmd in cmds: 
            await self.publish("mc.post", cmd)
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
            
            cmd = """summon chicken $coords {NoGravity:1b,NoAI:1b,Tags:["guess"],Passengers:[{see_through:0b,id:"minecraft:text_display",text:'[{"text":"$pseudo","color":"white","bold":true},{"text":"\n$comment","color":"$color","bold":true}]',background:$background}],ActiveEffects:[{Id:14,Amplifier:1b,Duration:4000,ShowParticles:0b}]}"""
            cmd = cmd.replace("$pseudo", f"{name}:")
            cmd = cmd.replace("$comment", f"{comment}")
            cmd = cmd.replace("$coords", f"{self.coords}")
            cmd = cmd.replace("$color", f"{self.colors[self.color_index]}")
            cmd = cmd.replace("$background", f"{0}")
            print(cmd)
            await self.publish("mc.post", cmd)
            
            self.color_index += 1
            if self.color_index >= len(self.colors):
                self.color_index = 0
        
        await asyncio.sleep(1.3)
    
        
if __name__ == "__main__":
    action = Guesses()
    asyncio.run(action.run())

