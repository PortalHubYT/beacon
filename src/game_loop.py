import asyncio
from datetime import datetime
import random

import shulker as mc
from dill import dumps

from tools.pulsar import Portal
from tools.config import config

"""
Step 0: Start the timer set to 30s
Step 1: Pick a word
Step 2: Show the word 'hint' (_ _ _ _ _)
Step 3: Start drawing the word and finish at 25s
Step 4: Add winners to the bench
Step 5: End the game at 30s elasped or if the bench is full
"""

WORD_LIST = ["pomme", "chat", "voiture", "flan"]

class GameLoop(Portal):
    async def on_join(self):
        await self.place_camera()
        await self.game_loop()
    
    async def place_camera(self):
        """
        Places the camera in the world
        """
        
        camera_name = config.camera_name
        camera_pos = config.camera_pos
        
        # Place a redstone block under the camera
        f = lambda: mc.set_block(camera_pos.offset(y=-1), "redstone_block")
        await self.publish('mc.lambda', dumps(f))
        
        # Place the camera
        await self.publish('mc.post', f"tp {camera_name} {camera_pos}")
   
    async def new_round(self):
        await self.publish('gl.set_timer', config.round_time)
        await self.publish('gl.clear_hint')
        self.word = random.choice(WORD_LIST).upper()
        await self.publish('gl.show_hint', self.word)
        
        # Reset timer
        # Delete hint
        # Pick new word
        # Show hint
        # Start drawing
        
    async def game_loop(self):
        time = datetime.now()
        timer_value = config.round_time
        
        while True:
            
            if timer_value == 0:
                timer_value = config.round_time
                await self.new_round()
            
            one_second_elapsed = (datetime.now() - time).seconds >= 1
            
            if one_second_elapsed:
                time = datetime.now()
                timer_value -= 1
                await self.publish('gl.set_timer', timer_value)
    
        
if __name__ == "__main__":
    action = GameLoop()
    asyncio.run(action.run())

