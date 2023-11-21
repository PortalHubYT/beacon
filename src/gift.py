import asyncio
import random
import time
from pprint import pprint

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
CHAT_TEXT = CHAT_BUBBLE.offset(0.9, 1.12, 1)
CHAT_NAME = CHAT_TEXT.offset(0, 0.3, 0)

################################################################################

class Template(Portal):
    async def on_join(self):
        self.current_gifter = {
            "npc_id": None,
            "user": None
        }
        
        self.current_yaw = 0
        
        await self.subscribe("live.gift", self.on_gift)
        # await self.subscribe("live.comment", self.on_comment)
    
        await self.clean_gifters()
        await self.spawn_gifters()
        await self.loop_around()
        
    async def clean_gifters(self):
        await self.publish("mc.post", remove_model("gifters_platform"))
        await self.publish("mc.post", remove_model("gifters_chat"))
        await self.publish("mc.post", remove_model("gifters_text"))
        await self.publish("mc.post", remove_model("gifters_name"))
        await self.publish("mc.post", "npc remove all")
        
    async def spawn_gifters(self):
        
        cmds = get_spawn_commands("gifters_platform", PLATFORM)
        for cmd in cmds:
            await self.publish("mc.post", cmd)
        cmds = get_spawn_commands("gifters_chat", CHAT_BUBBLE)
        for cmd in cmds:
            await self.publish("mc.post", cmd)
        cmd = """summon text_display $pos {text:'{"text":"DEFAULT"}', Tags:["gifters_text"]}""".replace("$pos", str(CHAT_TEXT))
        await self.publish("mc.post", cmd)
        cmd = """summon text_display $pos {text:'{"text":"DEFAULT"}', Tags:["gifters_name"]}""".replace("$pos", str(CHAT_NAME))
        await self.publish("mc.post", cmd)
    
    async def on_comment(self, user):
        if user["user_id"] == self.current_gifter["user"]["user_id"]:
            cmd = ...
    
    async def on_gift(self, user):
        
        if self.current_gifter["npc_id"] != None:
            cmd = f"npc remove {self.current_gifter['npc_id']}"
            await self.publish("mc.post", cmd)
        
        def spawn_shopper(name, pos):
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
        f = lambda: spawn_shopper(name, pos)
        self.current_gifter["npc_id"] = await self.call("mc.lambda", dumps(f))
        self.current_gifter["user"] = user
    
    async def loop_around(self):
        
        i = 0
        while True:
            if self.current_gifter["npc_id"] == None:
                await asyncio.sleep(0.05)
                continue
            
            cmd = f"npc moveto --yaw {i} --id {self.current_gifter['npc_id']}"
            await self.publish("mc.post", cmd)
            await asyncio.sleep(0.1)
            i += 3
            rand = random.uniform(0, 1)
            if rand < 0.1:
                cmd = f"particle minecraft:electric_spark {PARTICLES} 0.2 0.45 0.2 0 1"
                await self.publish("mc.post", cmd)
            if i > 360:
                i = 0
        
if __name__ == "__main__":
    action = Template()
    asyncio.run(action.run())

