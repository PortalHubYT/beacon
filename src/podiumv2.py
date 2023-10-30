import asyncio
import importlib
import math
import random
import time

import shulker as mc
from dill import dumps

import tools.config
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
    def __init__(self, pos, texture, title, subtitle, sign_size = (1.5,1,0.1), translation = (0, 0, 0)):
        self.pos = pos
        self.texture = texture
        self.title = title
        self.subtitle = subtitle
        self.sign_size = sign_size
        self.translation = translation

    def update_text(self):
        pass

    

    def delete(self):
        pass    
        


class Podium(Portal):
    
    async def on_join(self):
        await self.reload_config()

        self.winner_ids = []
        random.seed()

        await self.subscribe("podium.spawn_winner", self.spawn_winner)
        await self.subscribe("podium.reset", self.reset_podium)
        await self.subscribe("podium.reload", self.reload_podium)
        await self.subscribe("podium.remove", self.remove_podium)
        await self.subscribe("gl.reload_config", self.reload_config)

        await self.reset_podium()
        

    async def reload_config(self):
        importlib.reload(tools.config)
        self.config = tools.config.config

    async def spawn_winner(self, args):
        def spawn_npc(score_template, name, pos, podium_pos, winstreak):
            print(f"spawn {name}")


            multiplicator = 1 + winstreak / 10
            win_colors = ["f", "e", "6", "c", "5", "d", "b"]
            if winstreak < len(win_colors):
                points_color = win_colors[winstreak]
            else:
                points_color = win_colors[-1]

            cmd = f'npc create --at {pos[0].x}:{pos[0].y}:{pos[0].z}:world --nameplate true "&{points_color}+{int(score_template[podium_pos -1] * multiplicator)}"'
            ret = mc.post(cmd)

            ret = (
                ret.replace("\x1b[0m", "")
                .replace("\x1b[32;1m", "")
                .replace("\x1b[33;1m", "")
                .replace("\n", "")
            )
            id = ret.split("ID ")[1].replace(").", "")

            mc.post(f"npc moveto --pitch {pos[1]} --yaw {pos[2]} --id {id}")
            mc.post(f"npc skin -s {name} --id {id}")

            return id

        pos, user, score, winstreak_amount = args
        # name = user["display"]

        # if pos > self.config.podium_size:
        #     cmd = (
        #         f'title {self.config.camera_name} actionbar {{"text":'
        #         + f'"#{pos} | {name[:14].center(14)} | +1pt | Score: {score}"}}'
        #     )
        #     await self.publish("mc.post", cmd)
        #     return

        # spawn_start = self.config.podium_pos.offset(y=-3, z=-0.2)
        # coords = self.coords_from_pos(spawn_start, pos - 1)

        # score_template = self.config.scores_template
        # f = lambda: spawn_npc(score_template, name, coords, pos, winstreak_amount)
        # ret = await self.call("mc.lambda", dumps(f))
        # self.winner_ids.append({"npc_id": ret, "user_id": user["user_id"]})

        # cmd = f"particle wax_on {coords[0]} 0 0 0 6 100 normal"
        # await self.publish("mc.post", cmd)
        # cmd = f"particle wax_off {coords[0]} 0 0 0 6 100 normal"
        # await self.publish("mc.post", cmd)


       
        # cmd = f'title {self.config.camera_name} actionbar {{"text":"#{pos} | {name[:14].center(14)} | +{self.config["scores_template"][pos - 1]}pt | Score: {score}"}}'
        # await self.publish("mc.post", cmd)

    async def remove_podium(self):
        origin = self.config.podium_pos
        pass
        
    async def build_podium(self):
        cmd = f"npc remove all"
        await self.publish("mc.post", cmd)

        origin = self.config.podium_pos
        for y in range(7):
            cmd = f"setblock {origin.offset(y=y * 2)} barrier"
            await self.publish("mc.post", cmd)

        pos1 = origin.offset(z=1)
        pos2 = origin.offset(y=20, z=1)
        zone = mc.BlockZone(pos1, pos2)
        cmd = f"fill {zone} light"
        await self.publish("mc.post", cmd)

        for i in range(6):
            cmd = f"npc create --at 4.8:{63+i*2}:18.5:world --nameplate false sasa"
            await self.publish("mc.post", cmd)
            cmd = f'summon text_display 0.5 69.5 27 {{alignment:"center",text:\'{{"text":"funyrom1","color":"gold"}}\',background:-16777216}}'

        def spawn_sign(sign):
            print(f"SALUT ICI SPAWN {sign}")
            text1 = f"summon text_display 5.5 74.5 19.00 {{Tags:[\"text1\"],transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[2f,2f,1f]}},text:'{{\"text\":\"Salut\"}}',background:16711680}}"
            mc.post(text1)

        players_sign = AnimatedSign(origin.offset(y=20), "stone", "funyrom", "funyrom1")
        f = lambda: spawn_sign(players_sign)
        await self.publish("mc.lambda", dumps(f))

    async def reset_podium(self):
        pass
    async def reload_podium(self):
        await self.reset_podium()
        await self.remove_podium()
        await self.reload_config()
        await self.build_podium()


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
