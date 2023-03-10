import asyncio
import sys
import os

from dill import loads
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

# Work around to be able to import from the same level folder 'tools'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.config import config, db
import shulker as mc

server_ip = config["server_ip"]
rcon_password = config["rcon_password"]
rcon_port = config["rcon_port"]
verbose = config["verbose"]

fail = f"Failed to connect to: {server_ip}:{rcon_port} (password: {rcon_password})"
success = f"Connected to: {server_ip}:{rcon_port} (password: {rcon_password})"


class Poster(ApplicationSession):
    async def onJoin(self, details):
        print("Trying to connect to minecraft server...")

        try:
            mc.connect(server_ip, rcon_password, port=rcon_port)
            print(success)
        except Exception as e:
            print(fail)
            print(f"Error: {e}")
            return

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
