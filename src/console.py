import asyncio
import readline
import datetime
import random

import shulker as mc
from dill import dumps

from tools.pulsar import Portal
from dispatcher import listeners

class Console(Portal):
    async def on_join(self):
        print("------------------CONSOLE------------------")

    async def on_exit(self):
        print("-------------------------------------------")
        exit(0)
        
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
            await self.on_exit()

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
            await self.on_exit()

        elif len(cmd.split(" ")) > 2 and cmd.split(" ")[0] == "mimic" and cmd.split(" ")[1] in listeners:
            action = cmd.split(" ")[1]
            amount = int(cmd.split(" ")[2])
            if len(cmd.split(" ")) > 3:
                time_between = float(cmd.split(" ")[3])
            else:
                time_between = 1
                
            with open('tools/random_comments.txt', 'r') as f:
                random_comments = f.readlines()
                
            with open('tools/random_pseudos.txt', 'r') as f:
                random_pseudos = f.readlines()
            
            random_gift = ["Diamond", "Gold", "Silver", "Bronze"]
            random_avatars = ["https://i.imgur.com/0Z0Z0Z0.png", "https://i.imgur.com/1Z1Z1Z1.png", "https://i.imgur.com/2Z2Z2Z2.png", "https://i.imgur.com/3Z3Z3Z3.png", "https://i.imgur.com/4Z4Z4Z4.png", "https://i.imgur.com/5Z5Z5Z5.png", "https://i.imgur.com/6Z6Z6Z6.png", "https://i.imgur.com/7Z7Z7Z7.png", "https://i.imgur.com/8Z8Z8Z8.png", "https://i.imgur.com/9Z9Z9Z9.png"]
            random_role = ["Moderator", "Top Gifter", "New Gifter", "Follower", None]
            
            start = datetime.datetime.now()
            for i in range(amount):
                random_name = random.choice(random_pseudos).strip()
                profile = {
                    "display": f'{i + 1}_{random_name}',
                    "nickname": f'{i + 1}_{random_name}',
                    "unique_id": f'{i + 1}_{random_name}',
                    "user_id": random.randint(100000000, 999999999),
                    "role": random.choice(random_role),
                    "avatars": random_avatars,
                    "followers": random.randint(0, 100000),
                    "following": random.randint(0, 100000),
                    "comment": random.choice(random_comments).strip(),
                    "gift": random.choice(random_gift),
                    "gift_value": random.randint(0, 100000),
                }
                
                await self.publish(f"live.{action}", profile)
                await asyncio.sleep(time_between)
                time_elapsed_seconds = (datetime.datetime.now() - start).total_seconds()
                print(f"{self.time(trimmed=True)} o-> {i + 1}/{amount} [{action}] in {round(time_elapsed_seconds, 2)}s", end="\r")
                
            print()
        
if __name__ == "__main__":
    action = Console()
    asyncio.run(action.run())
