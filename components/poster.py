import asyncio
import sys
import os
from dotenv import load_dotenv

import shulker as mc
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

from config import config, db

MINECRAFT_IP = os.getenv("MINECRAFT_IP")
MINECRAFT_RCON_PASSWORD = os.getenv("MINECRAFT_RCON_PASSWORD")
MINECRAFT_RCON_PORT = os.getenv("MINECRAFT_RCON_PORT")

fail = f"Failed to connect to: {MINECRAFT_IP}:{MINECRAFT_RCON_PORT} (password: {MINECRAFT_RCON_PASSWORD})"
success = f"Connected to: {MINECRAFT_IP}:{MINECRAFT_RCON_PORT} (password: {MINECRAFT_RCON_PASSWORD})"

regular_post_queue = pulsar.subscribe(prefix + "mc.post", "mc.post.reading")
lambda_post_queue = pulsar.subscribe(prefix + "mc.lambda", "mc.lambda.reading")

class Poster(ApplicationSession):
    async def onJoin(self, details):
        print("Trying to connect to minecraft server...")

        try:
            mc.connect(MINECRAFT_IP, MINECRAFT_RCON_PASSWORD, port=MINECRAFT_RCON_PORT)
            print(success)
        except Exception as e:
            print(fail)
            print(f"Error: {e}")
            return

        def post(cmd):
            ret = mc.post(cmd)
            if config.verbose:
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