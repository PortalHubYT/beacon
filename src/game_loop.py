import asyncio
import time
import random
import signal
import sys
import math
import os

random.seed()

import shulker as mc
from dill import dumps

from tools.pulsar import Portal
from tools.config import config
from tools.mimic import gen_fake_profiles

BANNED_WORDS = [
    "pig",
    "gorilla",
    "cow",
    "monkey",
    "banana",
    "penis",
    "donkey",
    "joint",
    "hamburguer",
]


def get_word_list():
    ls = os.listdir("svg/")
    words = [
        f.replace(".svg", "")
        for f in ls
        if (f.islower() and f.replace(".svg", "") not in BANNED_WORDS)
    ]
    return words


class GameLoop(Portal):
    async def on_join(self):
        self.word_list = get_word_list()
        self.force_next_round = False
        self.rush_round = False
        self.word = None
        self.painting_finished = False
        self.winners = []
        await self.place_camera()
        await self.subscribe("live.comment", self.on_comment)
        await self.subscribe("gl.reset_camera", self.place_camera)
        await self.subscribe("gl.reset_arena", self.reset_arena)
        await self.subscribe("gl.next_round", self.next_round)
        await self.subscribe("gl.fake_win", self.fake_win)
        await self.subscribe("painter.finished", self.on_painting_finished)
        await self.game_loop()

    async def on_painting_finished(self):
        self.painting_finished = True
        if len(self.winners) >= 5:
            self.rush_round = True

    async def fake_win(self):
        fake_winner = gen_fake_profiles(1)[0]
        fake_winner["comment"] = self.word
        fake_winner["display"] = fake_winner["display"][2:]
        await self.on_comment(fake_winner)

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

    async def on_comment(self, user):
        if user["comment"].lower() != self.word:
            print(f"[{self.word}] {user['display']}: {user['comment']}")
            return
        else:
            print(f"[{self.word}]----> Correct guess from [{user['display']}]")

        if user["user_id"] in self.winners:
            print(f"-> [{user['display']}] already won")
            return

        self.winners += [user["user_id"]]
        if len(self.winners) == 5:
            print(f"about to rush painting, {self.painting_finished}")
            if not self.painting_finished:
                print("WE ARE SENDING RUSH PAINT")
                await self.publish("gl.rush_paint")

        scores_template = config.scores_template
        if len(self.winners) - 1 < len(scores_template):
            points_won = scores_template[len(self.winners) - 1]
        else:
            points_won = 1

        score = await self.call(
            "db", ("add_and_get_user_score", points_won, user["user_id"])
        )
        if (score % 100) - points_won < 0:
            cmd = f'title {config.camera_name} subtitle {{"text":"For reaching {score} points","color":"green"}}'
            await self.publish("mc.post", cmd)

            cmd = f'title {config.camera_name} title {{"text":"GG {user["display"]}","color":"green"}}'
            await self.publish("mc.post", cmd)

        if not score:
            print(
                f"-> Error: user_id [{user['user_id']}] nickname: [{user['display']}] was NOT FOUND in db, adding it now"
            )

            await self.publish("db", ("add_user", user))
            score = points_won + random.randint(0, 100)

        await self.publish(
            "gl.spawn_winner", (len(self.winners), user["display"], score)
        )

    async def before_round(self):
        await self.publish("painter.stop")
        await self.publish("gl.clear_hint")
        await self.publish("gl.clear_svg")
        await self.publish("gl.reset_podium")

        await self.publish("gl.set_timer", 100)
        cmd = f"bossbar set minecraft:timer visible true"
        await self.publish("mc.post", cmd)

    async def round(self):
        self.word = await self.new_word()

        await asyncio.sleep(1)
        self.winners = []
        print("--------------------------------------")
        print("-> New round with:", self.word)
        print("--------------------------------------")
        hint = "".join(["_" if c.isalnum() else c for c in self.word])

        self.painting_finished = False
        await self.publish("gl.paint_svg", self.word)

        self.rush_round = False
        start_round = time.time()
        while start_round + config.round_time > time.time():
            delta = time.time() - start_round
            round_progress = int(delta / config.round_time * 100)

            if self.rush_round == True:
                start_round -= 2

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

            await asyncio.sleep(0.3)
        self.rush_round = False

    async def after_round(self):
        self.force_next_round = False
        await self.publish("painter.stop")
        await self.publish("gl.print_hint", self.word)
        # display full hint
        # display title with winner
        cmd = f"bossbar set minecraft:timer visible false"
        await self.publish("mc.post", cmd)

        cmd = (
            f'title {config.camera_name} title {{"text":"Round over","color":"green"}}'
        )
        await self.publish("mc.post", cmd)

        cmd = f'title {config.camera_name} subtitle "found by {len(self.winners)} players"'
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
