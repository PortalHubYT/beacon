import asyncio
import sys
import os

from dill import loads
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

        print("Trying to connect to minecraft server...")
        
        try:
          mc.connect(server_ip, rcon_password, port=rcon_port)
        except ConnectionRefusedError:
          print(f"Failed to connect to server: {server_ip}:{rcon_port} (password: {rcon_password})")
          return
        except ConnectionResetError:
          print(f"Failed to connect to server: {server_ip}:{rcon_port} (password: {rcon_password})")
          return
        
        print(f"Connected to server: {server_ip}:{rcon_port} (password: {rcon_password})")

        def post(cmd):
            ret = mc.post(cmd)
            if verbose:
              print(f"===============")
              print(f"[CMD]->[{cmd}]")
              print(f"[RET]->[{ret}]")
              print(f"===============")
            return ret

        def lambda_post(cmd):
          instruction = loads(cmd)
          ret = instruction()
          return str(ret)
        
        await self.register(post, "mc.post")
        await self.subscribe(post, "mc.post")
        
        await self.register(lambda_post, "mc.lambda")
        await self.subscribe(lambda_post, "mc.lambda")
        
        print(f"Poster is ready to operate!")
    
if __name__ == "__main__":
    print(f"Starting Poster...")
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    print(runner.run(Poster))