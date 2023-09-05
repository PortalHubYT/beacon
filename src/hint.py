import asyncio
import random

import shulker as mc
from dill import dumps

from tools.config import config
from tools.pulsar import Portal

class Hint(Portal):
    async def on_join(self):
        self.revealed = []
        
        # Clean up leftovers
        cmd = f"sudo {config.camera_name} //replacenear 100 blackstone,blackstone_slab,blackstone_stairs,blackstone_wall air"
        await self.publish('mc.post', cmd)
        
        await self.subscribe("gl.show_hint", self.show_hint)
        await self.subscribe("gl.clear_hint", self.clear_hint)
        await self.subscribe("gl.reveal_random_letter", self.reveal_random_letter)
    
    async def show_hint(self, word):
        """
        Prints the hint on the screen, by replacing the letters of the chosen word with "_"
        Offsets the printed text to be centered on the camera, stores the zone of the hint
        in self.hint_zone
        """
        
        hint_distance = config.hint_distance
        hint_height = config.hint_height
        camera_pos = config.camera_pos
        
        hint = ""
        for i, char in enumerate(word):
            if i in self.revealed or char == " ":
                hint += char
            else:
                hint += "_"
                    
        def print_hint_get_zone():
            hint_pos = mc.BlockCoordinates(camera_pos.x, camera_pos.y + hint_height, camera_pos.z - hint_distance)
            
            status = mc.meta_set_text(
                hint,
                mc.BlockCoordinates(0, 0, 0),
                ["quartz"],
                "mixed",
                "east",
                mc.BlockHandler("replace"),
                0,
                mc.Block("air"),
                "minecraft",
            )
            zone = status["zone"]
            hint_pos = hint_pos.offset(x = -((zone.pos2.x - zone.pos1.x) / 2))
            
            status = mc.set_text(hint, hint_pos)
            return status["zone"]
        
        print(f"-> Showing hint for word '{word}'")
        f = lambda: print_hint_get_zone()
        zone = await self.call('mc.lambda', dumps(f))

        zone_tuples = zone.split(' ')
        
        corner_1_coords = zone_tuples[:len(zone_tuples)//2]
        corner_1 = mc.BlockCoordinates(*corner_1_coords)
        
        corner_2_coords = zone_tuples[len(zone_tuples)//2:]
        corner_2 = mc.BlockCoordinates(*corner_2_coords)
        
        self.hint_zone = mc.BlockZone(corner_1, corner_2)
        self.hint_word = word
    
    async def clear_hint(self):
        """
        Clears the hint zone by filling it with air
        """
        if hasattr(self, 'hint_zone'):
            print("-> Clearing hint zone")
            
            await self.publish('mc.post', f"fill {self.hint_zone} air")
        else:
            print("-> No hint zone to clear")

    async def reveal_random_letter(self):
        """
        Reveals a random letter from the hint word
        """
        
        word = self.hint_word
        to_reveal = None
        
        while to_reveal is None:
            index = random.randint(0, len(word) - 1)
            if index not in self.revealed and word[index] != " ":
                to_reveal = (word[index], index)
                
        self.revealed.append(to_reveal[1])
        await self.show_hint(word) 
     
        
if __name__ == "__main__":
    action = Hint()
    asyncio.run(action.run())

