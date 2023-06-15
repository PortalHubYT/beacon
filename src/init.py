import asyncio
import shulker as mc
from dill import dumps

from tools.pulsar import Portal
from tools.config import config
from tools.database import db

class Setup(Portal):
    async def on_join(self):
        
        if False: db.reset_database(confirm=False)
        
        print(f"Database is empty: {db.check_tables_empty()}")
        
        cmds = [
            f"tp {config.camera_name} {config.camera_pos}",
            f"gamemode creative {config.camera_name}",
            f"gamerule doDaylightCycle false",
            f"time set 6000",
            f"gamerule doWeatherCycle false",
            f"weather clear",
        ]
        
        for cmd in cmds:
            await self.publish('mc.post', cmd)
        
        exit(0)
        
if __name__ == "__main__":
    action = Setup()
    asyncio.run(action.run())

