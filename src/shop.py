import asyncio
from pprint import pprint

import shulker as mc
from dill import dumps

import tools.config
from models.spawn_helper import get_spawn_commands, remove_model
from tools.pulsar import Portal

################################################################################

GIFTER_PLATFORM_OFFSET = (0.7, -4.8, -10)
GIFTER_CHAT_OFFSET = (-0.7, -2.01, -10)

################################################################################

class Template(Portal):
    async def on_join(self):
        await self.subscribe("live.gift", self.on_gift)
        await self.subscribe("live.comment", self.on_comment)
    
        self.current_shopper = None
        await self.clean_podium()
        await self.spawn_podium()
        exit()
        
    async def clean_podium(self):
        await self.publish("mc.post", remove_model("gifters_platform"))
        await self.publish("mc.post", remove_model("gifters_chat"))
    
    async def spawn_platform(self):
        camera_pos: mc.BlockCoordinates = tools.config.config.camera_pos
        cmds = get_spawn_commands("gifters_platform", camera_pos.offset(*GIFTER_PLATFORM_OFFSET))
        for cmd in cmds:
            await self.publish("mc.post", cmd)
        cmds = get_spawn_commands("gifters_chat", camera_pos.offset(*GIFTER_CHAT_OFFSET))
        for cmd in cmds:
            await self.publish("mc.post", cmd)
            
    async def spawn_podium(self):
        await self.spawn_platform()
        
    async def on_comment(self, user):
        pass

    async def on_gift(self, user):
        name = "Lora"
        
        def spawn_shopper(self, name, pos):
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
            print(mc.post(f"npc moveto --x {x - 2} --yaw 30 --id {id}"))
        
        f = lambda: spawn_shopper(name)
        print(f"-> Adding {user['display']} to the gift queue")
        await self.publish("mc.lambda", dumps(f))
    
if __name__ == "__main__":
    action = Template()
    asyncio.run(action.run())

