import asyncio
import random
import textwrap
import time
from pprint import pprint
import math

import shulker as mc
from dill import dumps

from models.spawn_helper import get_spawn_commands, remove_model
from tools.config import config
from tools.pulsar import Portal

################################################################################

CAMERA_POS = config.camera_pos

PLATFORM =  CAMERA_POS.offset(0.45, -4.5, -10)

CHARACTER = PLATFORM.offset(0.88, 1, 1.75)
PARTICLES = CHARACTER.offset(0.06, 1, 0.5)

CHAT_BUBBLE = PLATFORM.offset(-1.3, 2.27, 0)
CHAT_TEXT = CHAT_BUBBLE.offset(2, 0.8, 1)

################################################################################

class Gift(Portal):
    async def on_join(self):
        self.current_gifter = {
            "npc_id": None,
            "user": None
        }
        
        self.current_yaw = 0
        self.chat_spawn_time = None
        
        await self.subscribe("live.gift", self.on_gift)
        await self.subscribe("live.comment", self.on_comment)
        await self.subscribe("gift.spawn_platform", self.spawn_platform)
        await self.subscribe("gift.spawn_gifter", self.spawn_gifter)
        await self.subscribe("gift.spawn_chat", self.spawn_chat)
        await self.subscribe("gift.remove_chat", self.remove_chat)
    
        await self.clean_gifters()
        await self.spawn_platform()
        await self.loop()
        
    async def clean_gifters(self):
        await self.publish("mc.post", remove_model("gifters_platform"))
        await self.publish("mc.post", remove_model("gifters_chat"))
        await self.publish("mc.post", remove_model("gifters_text"))
        await self.publish("mc.post", remove_model("gifters_name"))

        
        # can't use because we don't keep the npc id between reloads
        # if self.current_gifter['npc_id'] != None:
        #     await self.publish("mc.post", f"npc remove {self.current_gifter['npc_id']}")
        await self.publish("mc.post", f"npc remove all")
    async def spawn_platform(self):
        print("spawn platform")
        
        cmds = get_spawn_commands("gifters_platform", PLATFORM)
        for cmd in cmds:
            await self.publish("mc.post", cmd)

        cmd = """/summon text_display ~ ~ ~ {start_interpolation:0,interpolation_duration:20,line_width:100,alignment:"center",Tags:["gifters_chat"],transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[1.3f,1.3f,1f]},text:'{"text":"$text","color":"#630E55","bold":true}',background:16711680}"""
        cmd = cmd.replace("/summon", "summon")
        cmd = cmd.replace("~ ~ ~", str(PLATFORM.offset(x=0.85, y=0.3, z=2)))
        cmd = cmd.replace("$text", "GIFTER")
        await self.publish("mc.post", cmd)

    async def spawn_gifter(self, user):
        print("spawn gifter")
        def spawn_gifter(name, pos):
            cmd = f'npc create --at {pos}:world --nameplate false {name}'
            
            ret = mc.post(cmd)
            ret = (
                ret.replace("\x1b[0m", "")
                .replace("\x1b[32;1m", "")
                .replace("\x1b[33;1m", "")
                .replace("\n", "")
            )
            id = ret.split("ID ")[1].replace(").", "")
            
            mc.post(f"npc gravity --id {id}")
            time.sleep(0.05)
            return id
        
        name = user['display']
        pos = str(CHARACTER).replace(" ", ":")
        f = lambda: spawn_gifter(name, pos)

        cmd = """/summon text_display ~ ~ ~ {start_interpolation:0,interpolation_duration:20,line_width:100,alignment:"center",Tags:["gifters_name"],transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[1.3f,1.3f,1f]},text:'{"text":"$text","color":"#3B0439","bold":true}',background:-2182660}"""
        cmd = cmd.replace("/summon", "summon")
        cmd = cmd.replace("~ ~ ~", str(PLATFORM.offset(x=0.85, y=0.8, z=2)))
        cmd = cmd.replace("$text", "GIFTER")
        await self.publish("mc.post", cmd)

        self.current_gifter["npc_id"] = await self.call("mc.lambda", dumps(f))
        self.current_gifter["user"] = user
        
        
    
    async def spawn_chat(self, chat):
        await self.remove_chat()
        self.chat_spawn_time = time.time()

        print("chat:", chat)
        def spawn_bubble(cmds):
            for cmd in cmds:
                print(mc.post(cmd))
        cmds = get_spawn_commands("gifters_chat", CHAT_BUBBLE)
        f = lambda: spawn_bubble(cmds)
        await self.publish("mc.lambda", dumps(f))


        chat = textwrap.wrap(chat, 16, max_lines=2, placeholder='...')

        
        if len(chat) == 1:
            cmd = """/summon text_display ~ ~ ~ {alignment:"center",Tags:["gifters_chat"],transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[2f,2f,1f]},text:'{"text":"$text","font":"uniform","color":"#1C1B18","bold":true}',background:16711680}"""
            cmd = cmd.replace("/summon", "summon")
            cmd = cmd.replace("~ ~ ~", str(CHAT_TEXT.offset(x=-0.05,y=0.35)))
            cmd = cmd.replace("$text", chat[0])
            await self.publish("mc.post", cmd)
        else: 
            cmd = """/summon text_display ~ ~ ~ {alignment:"center",Tags:["gifters_chat"],transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[1.7f,1.7f,1f]},text:'{"text":"$text","font":"uniform","color":"#1C1B18","bold":true}',background:16711680}"""
            cmd = cmd.replace("/summon", "summon")
            cmd = cmd.replace("~ ~ ~", str(CHAT_TEXT.offset(y=0.55)))
            cmd = cmd.replace("$text", chat[0])
            await self.publish("mc.post", cmd)
            cmd = """/summon text_display ~ ~ ~ {alignment:"center",Tags:["gifters_chat"],transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[1.7f,1.7f,1f]},text:'{"text":"$text","font":"uniform","color":"#1C1B18","bold":true}',background:16711680}"""
            cmd = cmd.replace("/summon", "summon")
            cmd = cmd.replace("~ ~ ~", str(CHAT_TEXT.offset(y=0.2)))
            cmd = cmd.replace("$text", chat[1])
            await self.publish("mc.post", cmd)


    async def remove_chat(self):
        cmd = 'kill @e[tag=gifters_chat]'
        await self.publish("mc.post", cmd)

    
    async def on_comment(self, user):
        if user["user_id"] == self.current_gifter["user"]["user_id"]:
            cmd = ...
    
    async def on_gift(self, user):
        
        if self.current_gifter["npc_id"] != None:
            cmd = f"npc remove {self.current_gifter['npc_id']}"
            await self.publish("mc.post", cmd)

        self.current_yaw = 0
        await self.spawn_gifter(user)
    
    async def loop(self):
        def compute_position(x, y, angle, distance):
            angle_rad = math.radians(angle)
            new_x = x + distance * math.cos(angle_rad)
            new_y = y + distance * math.sin(angle_rad)
            return (new_x, new_y)
        
    
        while True:
            #nametag:
            nametag_x, nametag_z = compute_position(CHARACTER.x, CHARACTER.z +0.7, self.current_yaw + 15, 0.1)
            cmd = f"tp @e[tag=gifters_name] {nametag_x} {CHARACTER.y + 1} {nametag_z}"
            await self.publish("mc.post", cmd)

            #turntable
            if self.current_gifter["npc_id"] == None:
                await asyncio.sleep(0.1)
                continue
            
            cmd = f"npc moveto --yaw {self.current_yaw} --id {self.current_gifter['npc_id']}"
            await self.publish("mc.post", cmd)
            await asyncio.sleep(0.1)
            self.current_yaw += 3
            rand = random.uniform(0, 1)
            if rand < 0.1:
                cmd = f"particle minecraft:electric_spark {PARTICLES} 0.2 0.45 0.2 0 1"
                await self.publish("mc.post", cmd)
            if self.current_yaw > 360:
                self.current_yaw = 0

            #chat
            if self.chat_spawn_time != None:
                if time.time() - self.chat_spawn_time > 5:
                    await self.remove_chat()
                    self.chat_spawn_time = None
        
if __name__ == "__main__":
    action = Gift()
    asyncio.run(action.run())

