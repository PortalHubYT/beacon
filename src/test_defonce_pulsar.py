import asyncio
import shulker as mc
from dill import dumps

from tools.pulsar import Portal

class Template(Portal):
    i = 0
        
    async def loop(self):
        self.i += 1
        print(f"-> {self.i}")
        
        tasks = []
        for _ in range(30):
            task = asyncio.create_task(self.publish("mcpopo", self.i))
            tasks.append(task)
        
        await asyncio.gather(*tasks)

        
if __name__ == "__main__":
    action = Template()
    asyncio.run(action.run(), debug=True)

