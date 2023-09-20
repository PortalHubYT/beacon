import asyncio
import time
import shulker as mc
from dill import loads

from tools.config import config
from tools.pulsar import Portal

class Poster(Portal):
    async def on_join(self):
        self.rcon_connect()

        print("o) Subscribing to mc.post")
        await self.subscribe("mc.post", self.normal_post)

        print("o) Subscribing to mc.lambda")
        await self.subscribe("mc.lambda", self.lambda_post)

        print("o) Registering mc.post")
        await self.register("mc.post", self.normal_post)

        print("o) Registering mc.lambda")
        await self.register("mc.lambda", self.lambda_post)

        print("-> Poster is ready and listening to pulsar")

    def normal_post(self, cmd):
        if not isinstance(cmd, str):
            print(f"-> [ERROR] Command is not a string: {cmd}")
            return None

        ret = mc.post(cmd)
        if config.verbose:
            print(f"===============")
            print(f"[CMD]->[{cmd}]")
            print(f"[RET]->[{ret}]")
            print(f"===============")
        return ret

    def lambda_post(self, serialized_lambda):
        instruction = loads(serialized_lambda)
        ret = instruction()
        if type(ret) is list:
            return ", ".join(ret)
        else:
            return str(ret)

    def rcon_connect(self):
        server_status = (
            f"{config.server_ip}:{config.rcon_port} (password: {config.rcon_password})"
        )
        success = f"-> Connected to: {server_status}"
        fail = f"-> Failed to connect to: {server_status}"

        try:
            mc.connect(config.server_ip, config.rcon_password, port=config.rcon_port)
            print(success)
        except Exception as e:
            print(fail)
            exit(f"Error: {e}")


if __name__ == "__main__":
    action = Poster()
    while True:
        try:
            asyncio.run(action.run())
        except Exception as e:
            error_msg = f"An error occurred: {e}"
            print(error_msg)
            print("-> Restarting in 1 seconds...")
            time.sleep(1)
