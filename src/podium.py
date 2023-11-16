import asyncio
import importlib
import math
import random
import time

import shulker as mc
from dill import dumps

import models.podium_box as podium_box
import tools.config
from models.podium_box import data as box_data
from tools.pulsar import Portal

# """
# /summon block_display 5.7 76.3 19.3 {Tags:["sign1"],Passengers:[{id:"minecraft:text_display",billboard:"center",alignment:"center",Tags:["text1"],Passengers:[{id:"minecraft:text_display",billboard:"center",alignment:"center",Tags:["subtext1"],transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0.8f,0.2f,0.2f],scale:[1f,1f,1f]},text:'{"text":"viewers","color":"white"}',background:16711680}],transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0.8f,0.4f,0.2f],scale:[1.5f,1.5f,1f]},text:'{"text":"563","color":"white","bold":true}',background:16711680}],transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[1.7f,1f,0.1f]},block_state:{Name:"minecraft:oak_planks"}}
# """
# """
# /data merge entity @e[type=block_display,limit=1,tag=sign1] {start_interpolation:-1,interpolation_duration:5,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-2f,0f,0f],scale:[1.7f,1f,0.1f]}}
# """
# "/data merge entity @e[type=text_display,limit=1,tag=text1] {start_interpolation:-1,interpolation_duration:5,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-1.2f,0.4f,0.2f],scale:[1.5f,1.5f,1f]}}"
# "/data merge entity @e[type=text_display,limit=1,tag=subtext1] {start_interpolation:-1,interpolation_duration:5,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-1.2f,0.2f,0.2f],scale:[1f,1f,1f]}}"

class AnimatedSign():
    def __init__(self, pos, texture, text, subtext, suffix, sign_size = (1.5,1,0.1), translation = (0, 0, 0)):
        self.pos = pos
        self.texture = texture
        self.text = text
        self.subtext = subtext
        self.suffix = suffix
        self.sign_size = sign_size
        self.translation = translation


class Podium(Portal):
    
    async def on_join(self):
        await self.reload_config()

        self.winner_ids = []
        random.seed()

        await self.subscribe("podium.spawn_winner", self.spawn)
        await self.subscribe("live.viewer_update", self.update_signs)
        await self.subscribe("podium.reload", self.reload_podium)
        await self.subscribe("podium.reset", self.reset_podium)
        await self.subscribe("podium.remove", self.remove_podium)
        await self.subscribe("gl.reload_config", self.reload_config)


    async def reload_config(self):
        importlib.reload(tools.config)
        self.config = tools.config.config

    async def spawn(self, args):
    
        def spawn_npc(x, y, skin):
            pos = f"{x}:{y}:18.7"
            cmd = f'npc create --at {pos}:world --nameplate false {skin}'
            
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


        def spawn_box(x, y, podium_pos, name, score, points, box_data=box_data):
            
            # ##SUPER CURSED DEV CODE
            # import importlib

            # import models.podium_box as podium_box
            # importlib.reload(podium_box)
            # box_data = podium_box.data

            # names = ["funyrom", "Yasbaltrine", "portalhub", "123456l8", "jeb"]
            # score = ["19856", "156", "123", "1", "0"]
            # points = ["11", "34", "100", "210", "1"]
            ############
            print(f"{x=},{y=},{podium_pos=},{name=},{score=},{points=}")
            
            for data in box_data:
                tags = [f"podium{podium_pos}", "podium"]
                
                if "$name" in data:
                    data = data.replace("$name", f"{name[:9]}").replace("uniform", "default")
                if "$pos" in data:
                    data = data.replace("$pos", f"{podium_pos + 1}")
                if "$score" in data:
                    data = data.replace("$score", f"{score}").replace("uniform", "default")
                if "$points" in data:
                    data = data.replace("Tags:[\"podium\"]", f"Tags:[\"podium\",\"points{podium_pos}\"]").replace("$points", f"+{points}").replace("uniform", "default")
                    tags.append(f"points{podium_pos}")
                    
                    x -= (3 - len(str(points))) * 0.1
                    
                box_command = f"summon block_display {x - 1} {y} 18 {{Tags:{tags}, teleport_duration:3, Passengers:[{data}]}}"
                ret = mc.post(box_command)


            tp_box_cmd = f"execute as @e[tag=podium{podium_pos}] at @s run tp @s ~-2.5 ~ ~"
            mc.post(tp_box_cmd)

            sound_cmd = f"execute as @e[type=player] at @s run playsound minecraft:entity.experience_orb.pickup master @s ~ ~ ~ 1 {0.4+(podium_pos*0.2)}"
            mc.post(sound_cmd)
            
            time.sleep(0.05)
            hide_points_cmd = f"data merge entity @e[type=text_display,limit=1,tag=points{podium_pos}] {{start_interpolation:30,interpolation_duration:10,transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0.8f,-0.1f,0f],scale:[1.5f,1.5f,1f]}}}}"
            mc.post(hide_points_cmd)

        pos, name, score, points_won = args

        x = 7.0
        y = 72.5 - (pos * 2.5)
        f = lambda: spawn_box(x + 0.47, y, pos, name, score, points_won)
        await self.publish("mc.lambda", dumps(f))
        
        f = lambda: spawn_npc(x+0.2, y+0.2, name)
        await self.publish("mc.lambda", dumps(f))

###################### DEV
        # await self.publish("mc.post", "npc remove all")
        # await self.publish("mc.post", "kill @e[type=!player,tag=podium]")
        # time.sleep(0.2)
        

        # names = ["funyrom", "funy", "portalhub", "herobrine", "jeb"]
        # for i in range(int(args)):
            

        
        #     time.sleep(0.2)

            
        
    async def reset_podium(self):
        await self.publish("mc.post", "npc remove all")

        tp_box_cmd = f"execute as @e[tag=podium] at @s run tp @s ~2.5 ~ ~"
        await self.publish("mc.post", tp_box_cmd) 
        time.sleep(0.2)
        await self.publish("mc.post", "kill @e[type=!player,tag=podium]")
 

    async def remove_podium(self):
        await self.publish("mc.post", "npc remove all")
        await self.publish("mc.post", "kill @e[type=!player,tag=podium]")
    
    async def update_signs(self, viewer_count):
        cmd = f"data merge entity @e[tag=text1,limit=1] {{text:'{{\"bold\":true,\"text\":\"{viewer_count}\"}}'}}"
        await self.publish("mc.post", cmd)


    async def build_signs(self):
        def spawn_sign(sign):
            background = f"summon block_display {sign.pos.x + 2.7} {sign.pos.y - 0.5} {sign.pos.z - 0.1} {{Tags:[\"background{sign.suffix}\",\"sign{sign.suffix}\",\"podium_sign\"],transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[2f,1.2f,0.1f]}},block_state:{{Name:\"minecraft:{sign.texture}\"}},teleport_duration:5}}"
            print(mc.post(background))

            text = f"summon text_display {sign.pos.x + 3.7} {sign.pos.y - 0.02} {sign.pos.z + 0.0} {{shadow:1b,Tags:[\"text{sign.suffix}\",\"sign{sign.suffix}\",\"podium_sign\"],transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[2f,2f,1f]}},text:'{{\"text\":\"{sign.text}\",\"bold\":true}}',background:16711680,teleport_duration:5}}"
            print(mc.post(text))

            subtext = f"summon text_display {sign.pos.x + 3.7} {sign.pos.y - 0.38} {sign.pos.z + 0.0} {{shadow:1b,Tags:[\"subtext{sign.suffix}\",\"sign{sign.suffix}\",\"podium_sign\"],transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[1.3f,1.3f,1f]}},text:'{{\"text\":\"{sign.subtext}\", \"color\":\"gold\",\"bold\":true}}',background:16711680,teleport_duration:5}}"
            print(mc.post(subtext))

            tp_background = f"execute at @e[limit=1,tag=background{sign.suffix}] run tp @e[limit=1,tag=background{sign.suffix}] ~-2.6 ~ ~"
            print(mc.post(tp_background))

            tp_text = f"execute at @e[limit=1,tag=text{sign.suffix}] run tp @e[limit=1,tag=text{sign.suffix}] ~-2.6 ~ ~"
            print(mc.post(tp_text))
            
            tp_subtext = f"execute at @e[limit=1,tag=subtext{sign.suffix}] run tp @e[limit=1,tag=subtext{sign.suffix}] ~-2.6 ~ ~"
            print(mc.post(tp_subtext))

        origin = self.config.podium_pos
        players_sign = AnimatedSign(origin.offset(y=17.5), "dark_oak_planks", "2354", "players", "1")
        f = lambda: spawn_sign(players_sign)
        await self.publish("mc.lambda", dumps(f))

        players_sign = AnimatedSign(origin.offset(y=16.2), "spruce_planks", "1.6x", "boost", "2")
        f = lambda: spawn_sign(players_sign)
        await self.publish("mc.lambda", dumps(f))



            

    

    async def reload_podium(self):
        await self.remove_podium()
        await self.reload_config()
        await self.build_signs()


if __name__ == "__main__":
    action = Podium()
    while True:
        try:
            asyncio.run(action.run())
        except Exception as e:
            error_msg = f"An error occurred: {e}"
            print(error_msg)
            print("-> Restarting in 1 seconds...")
            time.sleep(1)
