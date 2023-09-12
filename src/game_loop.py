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
from tools.database import db

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
    async def on_join(self):
        self.word_list = get_word_list()
        await self.place_camera()
        await self.subscribe("live.comment", self.on_comment)
        await self.subscribe("gl.reset_camera", self.place_camera)
        await self.subscribe("gl.reset_arena", self.reset_arena)
        await self.subscribe("gl.reset_database", self.reset_database)
        await self.game_loop()

    async def reset_arena(self):
        await self.publish("gl.clear_hint")
        await self.publish("gl.clear_svg")
        cmd = f"sudo {config.camera_name} //replacenear 1000 grass,grass_block,bedrock air"
        await self.publish("mc.post", cmd)

    async def reset_database(self):
        db.reset_database(confirm=True)

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

    def get_current_hint(self, hint, progress):
        word_letters = sum(c.isalnum() for c in self.word)
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
            hint[idx] = self.word[idx]
            hint = "".join(hint)
            revealed += 1

        return hint

    # score : 10  5
    async def on_comment(self, event):
        guess = event["comment"].strip().lower()
        print("guess:", guess, "word:", self.word)

        if guess == self.word:
            self.winners += [event["user_id"]]

            scores_template = [10, 5, 2]
            if len(self.winners) - 1 < len(scores_template):
                points_won = scores_template[len(self.winners) - 1]
            else:
                points_won = 1

            score = db.add_and_get_user_score(points_won, event["user_id"])

            print(event["nickname"], "won", points_won, "points", "score = :", score)
            await self.publish(
                "gl.spawn_winner", (len(self.winners), event["nickname"], score)
            )

    async def before_round(self):
        await self.publish("gl.clear_hint")
        await self.publish("gl.clear_svg")
        pass

    async def round(self):
        self.word = self.new_word()
        self.winners = []
        print("-> New round with:", self.word)
        hint = "".join(["_" if c.isalnum() else c for c in self.word])

        await self.publish("gl.paint_svg", self.word)

        start_round = time.time()
        while start_round + config.round_time > time.time():
            delta = time.time() - start_round
            round_progress = int(delta / config.round_time * 100)

            hint = self.get_current_hint(
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
