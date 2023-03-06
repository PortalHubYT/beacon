import asyncio
import sys
import os

from dotenv import load_dotenv
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

import shulker as mc

load_dotenv()
server_ip = os.getenv("SERVER_IP")
rcon_password = os.getenv("RCON_PASSWORD")
rcon_port = os.getenv("RCON_PORT")
verbose = os.getenv("VERBOSE")

verbose = False
debug = False


class Poster(ApplicationSession):
    async def onJoin(self, details):

        mc.connect(server_ip, rcon_password, port=rcon_port)
        print(f"Connected to server: {server_ip}:{rcon_port} (password: {rcon_password})")

        def post(cmd):
            ret = mc.post(cmd)
            if verbose:
              print(f"===============")
              print(f"[CMD]->[{cmd}]")
              print(f"[RET]->[{ret}]")
              print(f"===============")
            return ret

        await self.register(post, "minecraft.post")
        await self.subscribe(post, "minecraft.post")
        
        print(f"Poster is ready to operate!")
    
if __name__ == "__main__":
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(Poster)