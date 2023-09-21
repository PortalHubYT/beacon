import asyncio
import time
import random
import signal
import sys
import math
import os
import importlib
import re

import shulker as mc
from dill import dumps

import tools.config
from tools.pulsar import Portal
from tools.mimic import gen_fake_profiles
from tools.svg import get_word_list


class GameLoop(Portal):
    async def on_join(self):
        await self.reload_config()
        self.pause = False
        self.should_stop = False

        self.total_word_list = get_word_list(
            character_limit=self.config.word_len_limit,
            banned_words=self.config.banned_words,
        )
        self.amount_of_words = len(self.total_word_list)
        self.word_list = self.total_word_list.copy()

        self.word_filename = None
        self.round_word = None
        self.upcoming_word = await self.next_word()

        self.force_next_round = False
        self.rush_round = False
        self.painting_finished = False
        self.winners = []
        self.svg_ready = False

        self.previous_winners = []
        self.winstreakers = []
        self.winstreak_enabled = False

        await self.place_camera()

        await self.subscribe("live.comment", self.on_comment)
        await self.subscribe("gl.reset_camera", self.place_camera)
        await self.subscribe("gl.reset_arena", self.reset_arena)
        await self.subscribe("gl.next_round", self.next_round)
        await self.subscribe("gl.fake_win", self.fake_win)
        await self.subscribe("painter.finished", self.on_painting_finished)
        await self.subscribe("gl.change_next_word", self.change_next_word)
        await self.subscribe("painter.svg_ready", self.on_svg_ready)
        await self.subscribe("painter.joined", self.on_painter_joined)
        await self.subscribe("live.viewer_update", self.toggle_winstreak)
        await self.subscribe("gl.pause", self.toggle_pause)

        await self.subscribe("gl.clear_map", self.clear_map)
        await self.subscribe("gl.reload_map", self.reload_map)

        await self.game_loop()

    async def reload_config(self):
        importlib.reload(tools.config)
        self.config = tools.config.config
        await self.publish("gl.reload_config")

    async def reload_map(self):
        await self.publish("gl.pause")
        await self.place_camera()
        await self.publish("hint.reload")
        await self.publish("painter.reload_backboard")

    async def clear_map(self):
        pos_1 = self.config.camera_pos.offset(x=-50, z=-50)
        pos_2 = self.config.camera_pos.offset(x=50, z=50)
        for i in range(0, 255):
            pos_1.y = i
            pos_2.y = i
            await self.publish("mc.post", f"fill {pos_1} {pos_2} air")
            await self.publish(
                "mc.post", f"fill {pos_1.offset(x=-50)} {pos_2.offset(x=-50)} air"
            )
            await self.publish(
                "mc.post", f"fill {pos_1.offset(z=-50)} {pos_2.offset(z=-50)} air"
            )
            await self.publish(
                "mc.post", f"fill {pos_1.offset(x=50)} {pos_2.offset(x=50)} air"
            )
            await self.publish(
                "mc.post", f"fill {pos_1.offset(z=50)} {pos_2.offset(z=50)} air"
            )
            await self.publish(
                "mc.post",
                f"fill {pos_1.offset(x=-50, z=-50)} {pos_2.offset(x=-50, z=-50)} air",
            )
            await self.publish(
                "mc.post",
                f"fill {pos_1.offset(x=50, z=-50)} {pos_2.offset(x=50, z=-50)} air",
            )
            await self.publish(
                "mc.post",
                f"fill {pos_1.offset(x=-50, z=50)} {pos_2.offset(x=-50, z=50)} air",
            )
            await self.publish(
                "mc.post",
                f"fill {pos_1.offset(x=50, z=50)} {pos_2.offset(x=50, z=50)} air",
            )

    async def on_painter_joined(self):
        self.svg_ready = False
        await self.publish("painter.compute_svg", self.word_filename)

    async def on_painting_finished(self):
        self.painting_finished = True
        self.upcoming_word = await self.next_word()
        if len(self.winners) >= 5:
            self.rush_round = True

    async def on_svg_ready(self):
        print("-> SVG is ready")
        self.svg_ready = True

    async def fake_win(self):
        fake_winner = gen_fake_profiles(1)[0]
        fake_winner["comment"] = self.round_word
        fake_winner["display"] = fake_winner["display"][2:]
        print(f"[{self.round_word}]----> Correct guess from [{fake_winner['display']}]")
        await self.on_comment(fake_winner)

    async def next_round(self):
        print("-> Skipped to next round")
        self.force_next_round = True

    async def reset_arena(self):
        await self.publish("hint.clear")
        await self.publish("gl.clear_svg")
        cmd = f"sudo {self.config.camera_name} //replacenear 1000 grass,grass_block,bedrock air"
        await self.publish("mc.post", cmd)

    async def next_word(self):
        if len(self.word_list) == 0:
            self.word_list = get_word_list(
                character_limit=self.config.word_len_limit,
                banned_words=self.config.banned_words,
            )

        new_word = self.word_list.pop(0)
        self.word_filename = new_word + ".svg"

        if "_$" in new_word:
            new_word = new_word.split("_$")[0]

        self.svg_ready = False
        await self.publish("painter.compute_svg", self.word_filename)
        return new_word

    def signal_handler(self, sig, frame):
        # await self.publish("hint.clear") #if we get rid of async publish that's what we can do
        # await self.publish("gl.clear_svg")
        sys.exit(0)

    async def place_camera(self):
        print("-> Placing camera")
        await self.publish("mc.post", f"gamemode creative {self.config.camera_name}")
        await self.publish(
            "mc.post", f"tp {self.config.camera_name} {self.config.camera_pos}"
        )
        await self.publish("mc.post", f"gamerule doFireTick false")

    def get_current_hint(self, word, hint, progress):
        word_letters = sum(c.isalnum() for c in word)
        if progress > 100:
            progress = 100

        revealed_goal = math.floor(
            word_letters
            * ((self.config.letters_to_reveal_in_percentage / 100) * (progress / 100))
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

    async def toggle_winstreak(self, viewers):
        if viewers >= self.config.winstreak_minimum_viewers:
            self.winstreak_enabled = True
        else:
            self.winstreak_enabled = False

    async def handle_winstreak(self, user):
        user_id = user["user_id"]

        # Check if the user was a winner in the last round
        if user_id in self.previous_winners:
            existing_streak = next(
                (item for item in self.winstreakers if item["user_id"] == user_id), None
            )
            if existing_streak:
                existing_streak["count"] += 1
                print(
                    f"-> {user['display']}'s win streak is now {existing_streak['count']}"
                )
            else:
                self.winstreakers.append({"user_id": user_id, "count": 1})
                print(f"-> {user['display']}'s win streak has started at 1")

            return True
        else:
            # Remove any existing streak for this user
            self.winstreakers = [
                streak for streak in self.winstreakers if streak["user_id"] != user_id
            ]
            print(f"-> {user['display']}'s win streak has been reset.")

            return False

    def compute_winstreak_multiplier(self, winstreak):
        if winstreak == 0:
            return 1
        return 1 + (winstreak / 10)

    async def on_comment(self, user):
        if user["comment"].lower() != self.round_word:
            print(f"[{self.round_word}] {user['display']}: {user['comment']}")
            return
        else:
            print(f"[{self.round_word}]----> Correct guess from [{user['display']}]")

        if user["user_id"] in self.winners:
            print(f"-> [{user['display']}] already won")
            return

        self.winners += [user["user_id"]]
        if len(self.winners) == 5:
            if not self.painting_finished:
                await self.publish("gl.rush_paint")
            else:
                self.rush_round = True

        scores_template = self.config.scores_template
        if len(self.winners) - 1 < len(scores_template):
            points_won = scores_template[len(self.winners) - 1]
        else:
            points_won = 1

        winstreak_amount = 0

        if len(self.winners) <= 5 and await self.handle_winstreak(user):
            winstreak_amount = next(
                (
                    item
                    for item in self.winstreakers
                    if item["user_id"] == user["user_id"]
                ),
                None,
            )["count"]

        multiplier = self.compute_winstreak_multiplier(winstreak_amount)

        score = await self.call(
            "db", ("add_and_get_user_score", points_won * multiplier, user["user_id"])
        )

        if not score:
            print(
                f"-> Error: user_id [{user['user_id']}] nickname: [{user['display']}] was NOT FOUND in db, adding it now"
            )

            await self.publish("db", ("add_user", user))
            score = points_won + random.randint(0, 100)

        if (score % 100) - points_won < 0:
            cmd = f'title {self.config.camera_name} subtitle {{"text":"For reaching {score} points","color":"gold"}}'
            await self.publish("mc.post", cmd)

            cmd = f'title {self.config.camera_name} title {{"text":"GG {user["display"]}","color":"gold"}}'
            await self.publish("mc.post", cmd)

        await self.publish(
            "gl.spawn_winner", (len(self.winners), user, score, winstreak_amount)
        )

    async def before_round(self):
        await self.publish("painter.stop")
        await self.publish("hint.clear")
        await self.publish("gl.clear_svg")
        print("-> Before round svg_ready?", self.svg_ready)

        if self.round_word == self.upcoming_word:
            self.upcoming_word = await self.next_word()

        wait_time = 0
        while not self.svg_ready:
            await asyncio.sleep(0.1)
            wait_time += 0.1
            if wait_time > 10:
                cmd = f'title {self.config.camera_name} title {{"text":"Ran into an issue!","color":"red"}}'
                await self.publish("mc.post", cmd)
                cmd = f'title {self.config.camera_name} subtitle "restarting the game now :)"'
                await self.publish("mc.post", cmd)
                raise Exception(
                    "Waited too long for svg_ready, probably painter wasn't listening"
                )

        self.svg_ready = False
        if len(self.winners) != 0:
            self.previous_winners = self.winners[:5]
        print(f"-> In previous round, winners were: {self.previous_winners}")
        print(f"-> Current winstreakers: {self.winstreakers}")

        await self.publish("gl.reset_podium")
        await self.publish("timer.reset")

    def print_word(self):
        print("--------------------------------------")
        print(
            f"-> New round with: {self.word_filename} [{self.amount_of_words - len(self.word_list)}/{self.amount_of_words}]"
        )

        # Get next 3 words from the list.
        next_words = self.word_list[:3]

        # Handle the case where there might be fewer than 3 words left.
        if next_words:
            print("-> Next up:", ", ".join(next_words))
        else:
            print("-> End of word bag!")

        print("--------------------------------------")

    async def change_next_word(self, word):
        if word in self.total_word_list:
            print("-> Changing next word to: ", word)
            self.upcoming_word = word
            self.svg_ready = False
            await self.publish("painter.compute_svg", word + ".svg")
            self.word_list.insert(0, word)
            self.amount_of_words += 1
        else:
            print(f"-> {word} is not in the word list")

    async def round(self):
        await asyncio.sleep(1)
        self.winners = []
        self.print_word()
        self.round_word = self.upcoming_word
        hint = "".join(["_" if c.isalnum() else c for c in self.round_word])

        self.painting_finished = False
        await self.publish("gl.paint_svg", self.round_word)

        self.rush_round = False
        start_round = time.time()
        while start_round + self.config.round_time > time.time() and not self.pause:
            delta = time.time() - start_round
            round_progress = int(delta / self.config.round_time * 100)

            if self.rush_round == True:
                start_round -= 2

            hint = self.get_current_hint(
                self.round_word,
                hint,
                (round_progress / 100)
                / (self.config.drawing_finished_at_percentage / 100)
                * 100,
            )

            await self.publish("hint.print", hint)
            await self.publish("timer.set", 100 - round_progress)

            if self.force_next_round:
                await self.publish("painter.stop")
                break

            await asyncio.sleep(0.3)
        self.rush_round = False

    async def after_round(self):
        self.force_next_round = False
        await self.publish("painter.stop")
        await self.publish("hint.print", self.round_word)

        cmd = f'title {self.config.camera_name} title {{"text":"Round over","color":"green"}}'
        await self.publish("mc.post", cmd)

        cmd = f'title {self.config.camera_name} subtitle "found by {len(self.winners)} players"'
        await self.publish("mc.post", cmd)

        await asyncio.sleep(3.5)

        await self.publish("gl.clear_svg")

    async def toggle_pause(self):
        if self.pause:
            print(f"{'=' * 10}\n{'UNPAUSE'.center(10)}\n{'=' * 10}")
            self.pause = False
        else:
            print(f"{'=' * 10}\n{'PAUSE'.center(10)}\n{'=' * 10}")
            self.pause = True

    async def game_loop(self):
        signal.signal(signal.SIGINT, self.signal_handler)

        while self.should_stop is False:
            if self.pause:
                print("|| Gameloop is paused ")
                await asyncio.sleep(0.8)
                continue

            await self.before_round()
            await self.round()
            await self.after_round()
            await self.reload_config()


if __name__ == "__main__":
    action = GameLoop()
    while True:
        try:
            asyncio.run(action.run(), debug=True)
        except Exception as e:
            error_msg = f"An error occurred: {e}"
            print(error_msg)
            print("-> Restarting in 1 seconds...")
            time.sleep(1)
