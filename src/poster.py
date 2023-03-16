import asyncio
import datetime
import shulker as mc
from dill import loads

from tools.config import config
from tools.pulsar import PulsarWrapper
from tools._base_action import BaseAction

class Poster(BaseAction):
    async def on_join(self):
        self.rcon_connect()

        print("o) Subscribing to mc.post")
        await self.subscribe("mc.post", self.normal_post, subscription_name="mc.post.subscriber")

        print("o) Subscribing to mc.lambda")
        await self.subscribe("mc.lambda", self.lambda_post, subscription_name="mc.lambda.subscriber")

        print("o) Registering mc.post")
        await self.register("mc.post.ret", self.normal_post, subscription_name="mc.post.register")

        print("o) Registering mc.lambda")
        await self.register("mc.lambda.ret", self.lambda_post, subscription_name="mc.lambda.register")

        print("-> Poster is ready and listening to pulsar")
        
    def normal_post(self, cmd):
        print('-------------')
        print(f"{datetime.datetime.now()} Sending command to server: ")
        print(cmd)
        print('-------------')
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
        server_status = f"{config.server_ip}:{config.rcon_port} (password: {config.rcon_password})"
        success = f"-> Connected to: {server_status}"
        fail = f"-> Failed to connect to: {server_status}"

        try:
            mc.connect(config.server_ip, config.rcon_password, port=config.rcon_port)
            print(success)
        except Exception as e:
            print(fail)
            exit(f"Error: {e}")

if __name__ == "__main__":
    poster = Poster()
    asyncio.run(poster.run())