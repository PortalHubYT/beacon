import asyncio
import shulker as mc
import importlib

from dill import dumps

import tools.config
from tools.pulsar import Portal

"""
Spec:

- 1 match = 1 ensemble de X rounds
Chaque round les gens accumulent du score

- 1 round = 1 dessin

Tout est stocké dans la database pour qu'au relancement du script
on puisse reprendre là où on en était
"""
class Template(Portal):
    async def on_join(self):
        await self.reload_config()
    
        
    async def reload_config(self):
        importlib.reload(tools.config)
        self.config = tools.config.config
        
if __name__ == "__main__":
    action = Template()
    asyncio.run(action.run())

