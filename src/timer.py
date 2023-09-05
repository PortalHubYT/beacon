import asyncio
import shulker as mc
from dill import dumps

from tools.config import config
from tools.pulsar import Portal

class Timer(Portal):
    async def on_join(self):
        await self.subscribe("gl.timer", self.initialize_timer)
        await self.subscribe("gl.set_timer", self.set_timer)
        await self.subscribe("gl.show_timer", self.show_timer)
        await self.subscribe("gl.hide_timer", self.hide_timer)
        
    async def initialize_timer(self):
        """
        Creates the in-game bossbar that will be used as a timer 
        """
        
        print("-> Initializing timer")
        
        round_time = config.round_time
        f = lambda: mc.create_bossbar("timer", "Timer", value=round_time, color="red", style="progress", max=30, visible=True)
        await self.publish('mc.lambda', dumps(f))
        
    async def set_timer(self, value):
        """
        Sets the timer to the given value, by updating the in-game bossbar 
        """
        
        print(f"-> Setting timer to {value}")
        
        f = lambda: mc.set_bossbar("timer", "value", value)
        ret = await self.publish('mc.lambda', dumps(f))
    
    async def show_timer(self):
        """
        Shows the timer on the screen
        """
        
        print("-> Showing timer")
        
        f = lambda: mc.set_bossbar("timer", "visible", True)
        await self.publish('mc.lambda', dumps(f))
        
    async def hide_timer(self):
        """
        Hides the timer from the screen
        """
        
        print("-> Hiding timer")
        
        f = lambda: mc.set_bossbar("timer", "visible", False)
        await self.publish('mc.lambda', dumps(f))

        
if __name__ == "__main__":
    action = Timer()
    asyncio.run(action.run())

