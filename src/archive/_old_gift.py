import asyncio


from dill import dumps
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
import shulker as mc

from tools.pulsar import Portal
from tools.config import config
from tools.postgres import db


class Gift(Portal):
    async def on_join(self):
        print("Gift component loaded")

        async def on_gift(profile):
            print(f"{profile['gift_value']} gifted by {profile['display']}")
            await self.publish("db", ("add_user_gifted", profile["gift_value"], profile["user_id"]))

            name = profile["display"]
            if not name:
                return

            result = await self.call("db", ("get_user_gifted_value_since_last_reset", profile["user_id"]))
            print("RESULT GOT::", result)
            if result:
                print("result:", result)
                gifted_since_action = result
                print(
                    f"{name} has donated {gifted_since_action} coins since their last picture was drawn"
                )
            else:
                print(f"{name} has never donated before")
                return

            if gifted_since_action > config.gift_trigger:
                print("this user has donated enough to trigger a picture")
                print(
                    f"{name} reached {gifted_since_action} coins, drawing their picture"
                )

                await self.publish("db", ("reset_user_gifted_value_since_last_reset", profile["user_id"]))

        await self.subscribe("live.gift", on_gift)

        # async def next_gift():
        #     if queue:
        #         name, url = queue.pop(0)
        #         return (name, url)
        #     else:
        #         return None

        # await self.register("gift.next", next_gift)


if __name__ == "__main__":
    action = Gift()
    asyncio.run(action.run())
