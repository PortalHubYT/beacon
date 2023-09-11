import asyncio
import time
import random
import signal
import sys
import math
import os

import shulker as mc
from dill import dumps

from tools.pulsar import Portal
from tools.config import config

"""
Step 0: Start the timer set to 30s
Step 1: Pick a word
Step 2: Show the word 'hint' (_ _ _ _ _)
Step 3: Start drawing the word and finish at 25s
Step 4: Add winners to the bench
Step 5: End the game at 30s elasped or if the bench is full
"""

WORD_LIST = ["pomme", "chat", "voiture", "flan"]


def get_word_list():
    ls = os.listdir("svg/")
    return [f.replace(".svg", "") for f in ls]


class GameLoop(Portal):
    def __init__(self):
        super().__init__()
        self.word_list = get_word_list()

    async def on_join(self):
        await self.place_camera()
        await self.game_loop()
        await self.subscribe("live.join", self.on_comment)

    async def reset_arena(self):
        cmd = f"sudo {config.camera_name} //replacenear 1000 grass,grass_block,bedrock air"
        await self.publish("mc.post", cmd)

    def new_word(self):
        if len(self.word_list) == 0:
            self.word_list = get_word_list()
        return self.word_list.pop(random.randint(0, len(self.word_list) - 1))

    def signal_handler(self, sig, frame):
        # await self.publish("gl.clear_hint") #if we get rid of async publish that's what we can do
        # await self.publish("gl.clear_svg")
        sys.exit(0)

    async def place_camera(self):
        await self.publish("mc.post", f"gamemode spectator {config.camera_name}")
        await self.publish("mc.post", f"tp {config.camera_name} {config.camera_pos}")

    def get_current_hint(self, word, hint, progress):
        word_letters = sum(c.isalnum() for c in word)
        if progress > 100:
            progress = 100

        revealed_goal = math.floor(
            word_letters
            * ((config.letters_to_reveal_in_percentage / 100) * (progress / 100))
        )
        # this makes sure we don't try to display more letters
        revealed_goal = min(revealed_goal, word_letters)

        revealed = sum(c.isalnum() for c in hint)

        while revealed < revealed_goal:
            idxs_to_reveal = []
            for i, c in enumerate(hint):
                if c == "_":
                    idxs_to_reveal.append(i)

            idx = random.choice(idxs_to_reveal)

            # str are immutables need to pass as a list before going back to str
            hint = list(hint)
            hint[idx] = word[idx]
            hint = "".join(hint)
            revealed += 1

        return hint

    async def on_comment(self, comment_event):
        print("comment_event", comment_event)

    async def before_round(self):
        await self.publish("gl.clear_hint")
        await self.publish("gl.clear_svg")
        pass

    async def round(self):
        word = self.new_word()
        print("-> New round with:", word)
        hint = "".join(["_" if c.isalnum() else c for c in word])

        await self.publish("gl.paint_svg", word)

        start_round = time.time()
        while start_round + config.round_time > time.time():
            delta = time.time() - start_round
            round_progress = int(delta / config.round_time * 100)

            hint = self.get_current_hint(
                word,
                hint,
                (round_progress / 100)
                / (config.drawing_finished_at_percentage / 100)
                * 100,
            )

            await self.publish("gl.print_hint", hint)

            await self.publish("gl.set_timer", 100 - round_progress)

            await asyncio.sleep(0.3)

    async def after_round(self):
        await self.publish("gl.clear_hint")
        await self.publish("gl.clear_svg")
        time.sleep(3)

    async def game_loop(self):
        signal.signal(signal.SIGINT, self.signal_handler)

        game_on = True
        while game_on:
            await self.before_round()
            await self.round()
            await self.after_round()


if __name__ == "__main__":
    action = GameLoop()
    asyncio.run(action.run())
