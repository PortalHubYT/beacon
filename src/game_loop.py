import asyncio
import time
import random
import signal
import sys
import math
import os

import names
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
    return [f.replace(".svg", "").lower() for f in ls]


class GameLoop(Portal):
    async def on_join(self):
        self.word_list = get_word_list()
        self.force_next_round = False
        self.word = None
        await self.place_camera()
        await self.subscribe("live.win", self.on_win)
        await self.subscribe("gl.reset_camera", self.place_camera)
        await self.subscribe("gl.reset_arena", self.reset_arena)
        await self.subscribe("gl.next_round", self.next_round)
        await self.subscribe("dispatcher.get_word", self.send_word)
        await self.game_loop()

    async def next_round(self):
        print("-> Skipped to next round")
        self.force_next_round = True

    async def reset_arena(self):
        await self.publish("gl.clear_hint")
        await self.publish("gl.clear_svg")
        cmd = f"sudo {config.camera_name} //replacenear 1000 grass,grass_block,bedrock air"
        await self.publish("mc.post", cmd)

    async def new_word(self):
        if len(self.word_list) == 0:
            self.word_list = get_word_list()
        new_word = self.word_list.pop(random.randint(0, len(self.word_list) - 1))
        await self.publish("gl.new_word", new_word)
        return new_word

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

    async def on_win(self, event):
        print("-> Winner:", event["nickname"])
        if event["user_id"] in self.winners:
            print("-> Already won")
            return
        self.winners += [event["user_id"]]

        scores_template = config.scores_template
        if len(self.winners) - 1 < len(scores_template):
            points_won = scores_template[len(self.winners) - 1]
        else:
            points_won = 1

        print("Before DB CALL")
        score = await self.call(
            "db", ("add_and_get_user_score", points_won, event["user_id"])
        )
        print("After DB CALL")
        if not score:
            print(
                f"Error: user_id {event['user_id']} nickname: {event['nickname']}  NOT FOUND IN DATABASE"
            )
            self.winners.pop()
            return

        print(event["nickname"], "won", points_won, "points", "score = :", score)
        await self.publish(
            "gl.spawn_winner", (len(self.winners), event["nickname"], score)
        )

    async def before_round(self):
        await self.publish("painter.stop")
        await self.publish("gl.clear_hint")
        await self.publish("gl.clear_svg")

        await self.publish("gl.set_timer", 100)
        cmd = f"bossbar set minecraft:timer visible true"
        await self.publish("mc.post", cmd)

    async def send_word(self):
        await self.publish("gl.new_word", self.word)

    async def round(self):
        triggers = [30, 60, 64, 65, 66]
        spawned_winners = 0

        self.word = await self.new_word()
        await asyncio.sleep(1)
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

            if self.force_next_round:
                await self.publish("painter.stop")
                break

            # if round_progress > triggers[spawned_winners] and spawned_winners < 5:
            #     spawned_winners += 1
            #     await self.publish(
            #         "gl.spawn_winner",
            #         (spawned_winners, names.get_full_name(), random.randrange(90) + 10),
            #     )

            await asyncio.sleep(0.3)

    async def after_round(self):
        self.force_next_round = False
        await self.publish("painter.stop")
        await self.publish("gl.print_hint", self.word)
        # display full hint
        # display title with winner
        cmd = f"bossbar set minecraft:timer visible false"
        await self.publish("mc.post", cmd)

        cmd = f'title {config.camera_name} title {{"text":"Round over","color":"red"}}'
        await self.publish("mc.post", cmd)

        cmd = f'title {config.camera_name} subtitle "The word was {self.word}"'
        await self.publish("mc.post", cmd)

        await asyncio.sleep(3.5)
        await self.publish("gl.clear_svg")
        await self.publish("gl.reset_podium")

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
