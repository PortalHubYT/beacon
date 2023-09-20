import asyncio
import shulker as mc
from dill import dumps
import importlib
import random

from tools.pulsar import Portal
from tools.mimic import gen_fake_profiles
import tools.config

import time


class Gift(Portal):
    async def on_join(self):
        await self.reload_config()
        
        self.gift_queue = []
        self.start_time = time.time()
        self.spawned_gifters = []
        
        await self.subscribe("gift.build_pipe", self.build_pipe)
        await self.subscribe("live.gift", self.on_gift)
        await self.subscribe("gift.fake_gift", self.fake_gift)
        await self.subscribe("gl.reload_config", self.reload_config)

        # await self.build_pipe()
 
    async def reload_config(self):
        importlib.reload(tools.config)
        self.config = tools.config.config
        
    async def fake_gift(self):
        fake_winner = gen_fake_profiles(1)[0]
        fake_winner["display"] = fake_winner["display"][2:]
        fake_winner["comment"] = "$fake_gift"
        await self.on_gift(fake_winner)
        
    async def on_gift(self, user):
        print(f"-> Adding {user['display']} to the gift queue")
        self.gift_queue.append(user)
        
    async def loop(self):
        
        print(f"-> There is {len(self.gift_queue)} gift(s) in the queue, elapsed time")
        print(f"-> Elapsed time until fake gift: {int(time.time() - self.start_time)}/{self.config.fake_gift_rate_seconds}s")
        
        # If there's any gift waiting in queue
        if len(self.gift_queue) > 0:
            print(f"-> Spawning gift for {self.gift_queue[0]['display']}")
            user = self.gift_queue.pop(0)
            await self.spawn_gifter(user)
        
        # Spawn a fake gifter
        elif time.time() - self.start_time > self.config.fake_gift_rate_seconds:
            self.start_time = time.time()
            print(f"-> Generating fake gift")
            await self.fake_gift()
        
        # We increment all the gifters second value by the spacing in seconds
        for i in range(len(self.spawned_gifters)):
            self.spawned_gifters[i][1] += self.config.gift_spacing_seconds
        
        # Prune the list of gifters, as we remove them in game
        new_spawned_gifters = []
        for gifter in self.spawned_gifters:
            if gifter[1] > self.config.gift_spacing_seconds * 3:
                print(f"-> Removing gifter {gifter[0]}")
                await self.publish("mc.post", f"npc remove {gifter[0]}")
            else:
                new_spawned_gifters.append(gifter)
                
        self.spawned_gifters = new_spawned_gifters
                
        await asyncio.sleep(self.config.gift_spacing_seconds)
        print('\n--------------------------\n')
        
    async def spawn_gifter(self, user):
        spawn_pos = str(self.config["podium_pos"].offset(x=-10, y=-2, z=-8))
        camera_name = self.config["camera_name"]
        path_to = str(self.config["podium_pos"].offset(x=10, y=-2, z=-8))
        name = user["display"]
        username = user["unique_id"]
        thx_message = self.config.gifter_message
        
        if self.config.gifters_name_styling == "random":
            colors = ["4", "5", '6', '7', '9', 'c', 'e']
            display =  "&" + random.choice(colors) + "&l"
        else:
            display = self.config.gifters_name_styling
            
        if user["comment"] == "$fake_gift":
            game_score = f"Your score: {random.randint(1, 150)} (Top {random.randint(1000, 10000)})"
        else:
            game_score = await self.call("db", ("get_user_score_and_rank", user["user_id"]))
            game_score = f"Your score: {game_score[1]} (Top {game_score[2]})"
        
        walkspeed = self.config.npc_walk_speed
        
        def spawn_npc(camera_name, spawn_pos, path_to, name, username, display, game_score, thx_message, walkspeed):
            
            spawn_pos = str(spawn_pos).replace(" ", ":")
            
            ret = mc.post(f"npc create &ks&r {display}{name} &ks&r --at {spawn_pos}:world")
            ret = ret.replace("\x1b[0m", "").replace("\x1b[32;1m", "").replace("\x1b[33;1m", "").replace("\n", "")
            id = ret.split("ID ")[1].replace(").", "")
            
            mc.post(f'npc hologram add "{game_score}" --id {id}')
            mc.post(f'npc hologram add "{thx_message}" --id {id}')
            
            mc.post(f"npc lookclose --id {id}")
            mc.post(f"npc pathopt --use-new-finder true --id {id}")
            mc.post(f"waypoints disableteleport --id {id}")
            mc.post(f"npc speed {walkspeed} --id {id}")
            mc.post(f"npc skin -s {username} --id {id}")
            import time
            time.sleep(0.1)
            mc.post(f"sudo {camera_name} /npc pathto {path_to} --id {id}")
            mc.post(f"npc pathto {path_to} --id {id}")
            
            return id
        
        f = lambda: spawn_npc(camera_name, spawn_pos, path_to, name, username, display, game_score, thx_message, walkspeed)
        id = await self.call("mc.lambda", dumps(f))
        self.spawned_gifters.append([id, 0])

    async def build_pipe(self):
        pos1 = self.config["podium_pos"].offset(x=-5, y=-6, z=-10)
        pos2 = pos1.offset(x=-2, y=20, z=-2)

        zone = mc.BlockZone(pos1, pos2)
        f = lambda: mc.set_zone(zone, "barrier")
        await self.publish("mc.lambda", dumps(f))

        hole_pos1 = pos1.offset(x=-1, y=0, z=-1)
        hole_pos2 = pos2.offset(x=1, y=0, z=1)
        hole_zone = mc.BlockZone(hole_pos1, hole_pos2)
        f = lambda: mc.set_zone(hole_zone, "air")
        await self.publish("mc.lambda", dumps(f))


if __name__ == "__main__":
    action = Gift()
    asyncio.run(action.run())
