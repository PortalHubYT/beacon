import asyncio
import readline
import datetime

import shulker as mc
from dill import dumps

from tools.pulsar import Portal


class Console(Portal):
    async def on_join(self):
        print("------------------CONSOLE------------------")

    def time(self, trimmed=False):
        hour_minute = datetime.datetime.now().strftime("%H:%M")
        text = f"({hour_minute})> "
        if not trimmed:
            return text
        return text[:-2]
        
    async def loop(self):
        try:
            cmd = input(f'{self.time()}')
        except KeyboardInterrupt:
            print("-------------------------------------------")
            exit(0)

        # Send a regular minecraft command
        if cmd.startswith("/"):
            arg = cmd[1:]
            if arg:
                ret = await self.call("mc.post", arg)
                if ret:
                    print(f"{self.time(trimmed=True)} o-> [{ret}]")
            return
        
        # Exit the terminal
        elif cmd in ["q", "quit", "exit"]:
            print("-------------------------------------------")
            exit(0)


if __name__ == "__main__":
    action = Console()
    asyncio.run(action.run())
