import asyncio
import time
import shulker as mc
from dill import dumps
from tools.postgres import db
from tools.pulsar import Portal


class Database(Portal):
    async def on_join(self):
        self.exposed = []

        for method_name in dir(db):
            if not method_name.startswith("__"):
                method = getattr(db, method_name)
                if callable(method):
                    self.exposed.append(method_name)

        await self.register("$db", self.db_exposed)
        await self.subscribe("$db", self.db_exposed)
        print("-> Registered db_exposed")

        await self.subscribe("db", self.db_manager)
        await self.register("db", self.db_manager)
        print("-> Registered db_manager")

    def db_exposed(self):
        return self.exposed

    def db_manager(self, args):
        if type(args) is str:
            args = (args,)

        if (
            len(args) < 1
            or not isinstance(args[0], str)
            or not isinstance(args, tuple)
            or args[0] not in self.exposed
        ):
            print("The first argument of the tuple must be the method name")
            return None
        elif args[0] not in self.exposed:
            print("The method you are trying to call doesn't exist")
            return None
        method_name = args[0]
        other_args = args[1:]

        # We call the method on the object db
        method = getattr(db, method_name)

        return method(*other_args)


if __name__ == "__main__":
    action = Database()
    while True:
        try:
            asyncio.run(action.run(), debug=True)
        except Exception as e:
            error_msg = f"An error occurred: {e}"
            print(error_msg)
            print("-> Restarting in 1 seconds...")
            time.sleep(1)
