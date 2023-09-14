import asyncio
import shulker as mc
import subprocess
import os
import signal
import time
import sys
from dill import dumps


from tools.pulsar import Portal


class Zookeeper(Portal):
    async def on_join(self):
        self.last_ping = time.time()

        await self.subscribe("dispatcher.alive", self.on_alive)
        await self.run_dispatcher()

        while True:
            print("i can print here")
            if time.time() - self.last_ping > 10:
                print("-> Dispatcher is dead, restarting...")
                # await self.kill_dispatcher()
                # await self.run_dispatcher()
            time.sleep(5)

    async def on_alive(self):
        print("dispatcher IS ALIVE!!")
        self.last_ping = time.time()

    async def run_dispatcher(self):
        self.process = subprocess.Popen(["python3", "dispatcher.py"], shell=False)

    async def kill_dispatcher(self):
        os.kill(self.process.pid, signal.SIGTERM)
        time.sleep(2)
        if self.process.poll() is None:
            print("force kill")
            # If it's still running, forcefully terminate it
            os.kill(self.process.pid, signal.SIGKILL)


if __name__ == "__main__":
    action = Zookeeper()
    asyncio.run(action.run())
