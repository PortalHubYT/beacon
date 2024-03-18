import asyncio
import importlib
import math
import random
import time

import shulker as mc
from dill import dumps

import tools.config
from tools.pulsar import Portal


def get_sign_data(messages, pos):
    top_colors = ["yellow", "white", "gold", "black", "black"]

    a = f"""{{front_text:{{color:"white",has_glowing_text:1b,messages:['{{"text":"{messages[0]}", "color":"{top_colors[pos - 1]}"}}','{{"text":"{messages[1]}", "color":"{top_colors[pos - 1]}"}}','{{"text":"{messages[2]}", "color":"{top_colors[pos - 1]}"}}','{{"text":"{messages[3]}", "color":"{top_colors[pos - 1]}"}}']}}}} """
    return a


class Podium(Portal):
    async def on_join(self):
        await self.reload_config()

        self.winner_ids = []
        random.seed()

        await self.subscribe("podium.spawn_winner", self.spawn_winner)
        await self.subscribe("podium.reset", self.reset_podium)
        await self.subscribe("podium.reload", self.reload_podium)
        await self.subscribe("podium.remove", self.remove_podium)
        await self.subscribe("gl.reload_config", self.reload_config)

        await self.reset_podium()
        await self.publish("mc.post", "npc remove all")
        


    async def reload_config(self):
        importlib.reload(tools.config)
        self.config = tools.config.config

    def coords_from_pos(self, start, pos):
        # this code breaks for config.podium_size > 5
        # https://discord.com/channels/@me/678579998847926273/1150958377745256578
        if self.config.podium_size > 5:
            raise ValueError("config.podium_size > 5 not supported")

        pitch_delta = [-10, -5, 0, 5, 10]
        coords = mc.Coordinates(
            start.x, start.y, start.z, yaw=-30, pitch=pitch_delta[pos]
        )
        deltas = [-1.85, -0.7, 0.5, 1.7, 2.85]

        return coords.offset(x=deltas[pos]), coords.yaw, coords.pitch

    async def spawn_winner(self, args):
        def spawn_npc(score_template, name, pos, podium_pos, winstreak):
            print(f"spawn {name}")


            multiplicator = 1 + winstreak / 10
            win_colors = ["f", "e", "6", "c", "5", "d", "b"]
            if winstreak < len(win_colors):
                points_color = win_colors[winstreak]
            else:
                points_color = win_colors[-1]

            cmd = f'npc create --at {pos[0].x}:{pos[0].y}:{pos[0].z}:world --nameplate true "&{points_color}+{int(score_template[podium_pos -1] * multiplicator)}"'
            ret = mc.post(cmd)

            ret = (
                ret.replace("\x1b[0m", "")
                .replace("\x1b[32;1m", "")
                .replace("\x1b[33;1m", "")
                .replace("\n", "")
            )
            id = ret.split("ID ")[1].replace(").", "")

            mc.post(f"npc moveto --pitch {pos[1]} --yaw {pos[2]} --id {id}")
            mc.post(f"npc skin -s {name} --id {id}")

            return id

        pos, user, score, winstreak_amount = args
        name = user["display"]

        if pos > self.config.podium_size:
            cmd = (
                f'title {self.config.camera_name} actionbar {{"text":'
                + f'"#{pos} | {name[:14].center(14)} | +1pt | Score: {score}"}}'
            )
            await self.publish("mc.post", cmd)
            return

        spawn_start = self.config.podium_pos.offset(y=-3, z=-0.2)
        coords = self.coords_from_pos(spawn_start, pos - 1)

        score_template = self.config.scores_template
        f = lambda: spawn_npc(score_template, name, coords, pos, winstreak_amount)
        ret = await self.call("mc.lambda", dumps(f))
        self.winner_ids.append({"npc_id": ret, "user_id": user["user_id"]})

        cmd = f"particle wax_on {coords[0]} 0 0 0 6 100 normal"
        await self.publish("mc.post", cmd)
        cmd = f"particle wax_off {coords[0]} 0 0 0 6 100 normal"
        await self.publish("mc.post", cmd)

        sign_start = self.config.podium_pos.offset(
            x=math.floor(-self.config.podium_size / 2)
        )

        sign_message = [
            f"#{pos}",
            f"",
            f"{name}",
            f"{score} pts",
        ]

        data = get_sign_data(sign_message, pos)

        fire_pos = f"{coords[0].x - 0.5} {coords[0].y} {coords[0].z - 0.5}"
        if winstreak_amount >= 5:
            cmd = f'summon block_display {fire_pos} {{block_state:{{Name:"minecraft:soul_fire"}}}}'
        elif winstreak_amount >= 1:
            cmd = f'summon block_display {fire_pos} {{block_state:{{Name:"minecraft:fire"}}}}'
        await self.publish("mc.post", cmd)

        await self.publish(
            "mc.post", f"data merge block {sign_start.offset(x=pos)} {data}"
        )

        cmd = f'title {self.config.camera_name} actionbar {{"text":"#{pos} | {name[:14].center(14)} | +{self.config["scores_template"][pos - 1]}pt | Score: {score}"}}'
        await self.publish("mc.post", cmd)

    async def remove_podium(self):
        origin = self.config.podium_pos
        pos1 = origin.offset(x=-10, y=-10, z=-10)
        pos2 = origin.offset(x=10, y=10, z=10)
        zone = mc.BlockZone(pos1, pos2)
        cmd = f"fill {zone} air"
        await self.publish("mc.post", cmd)

    async def remove_all_npc(self):
        def remove_all_winners(winners):
            for winner in winners:
                cmd = f"npc remove {winner['npc_id']}"
                mc.post(cmd)

        winners = self.winner_ids
        f = lambda: remove_all_winners(winners)
        await self.publish("mc.lambda", dumps(f))

    async def reset_signs(self):
        sign_start = self.config.podium_pos.offset(
            x=math.floor(-self.config.podium_size / 2)
        )
        for x_offset, _ in enumerate(range(self.config.podium_size + 1)):
            sign_message = [
                f"#{x_offset}",
                "",
                "",
                "",
            ]
            data = get_sign_data(sign_message, x_offset)
            await self.publish(
                "mc.post", f"data merge block {sign_start.offset(x=x_offset)} {data}"
            )

    async def build_podium(self):
        origin = self.config.podium_pos

        ### BACKGROUND
        background_start = origin.offset(x=-self.config.podium_size * 2, y=-5, z=-20)
        background_block = mc.Block("end_portal")
        await self.publish(
            "mc.post",
            f"fill {background_start} {background_start.offset(x = self.config.podium_size * 4, z=18)} {background_block}",
        )

        barrier_block = mc.Block("barrier")
        await self.publish(
            "mc.post",
            f"fill {background_start.offset(y=1)} {background_start.offset(x = self.config.podium_size * 4, y=1, z=18)} {barrier_block}",
        )

        ###### SIGN LINE
        sign_line = []

        # front_text:{color:"orange",,}
        # /setblock 16 133 57 minecraft:oak_wall_hanging_sign[facing=south,waterlogged=false]{,is_waxed:0b}
        wood = mc.Block("oak_wood")
        sign = mc.Block("oak_wall_hanging_sign")
        sign.blockstate = mc.BlockState({"facing": "south"})

        sign_line.append(wood)
        for _ in range(self.config.podium_size):
            sign_line.append(sign)

        sign_line.append(wood)

        sign_start = origin.offset(x=math.floor(-self.config.podium_size / 2))
        for x_offset, block in enumerate(sign_line):
            await self.publish(
                "mc.post", f"setblock {sign_start.offset(x=x_offset)} {block}"
            )

            if block.id == mc.Block("oak_wall_hanging_sign").id:
                sign_message = [
                    f"#{x_offset}",
                    "",
                    "",
                    "",
                ]
                data = get_sign_data(sign_message, x_offset)

                cmd = f"data merge block {sign_start.offset(x=x_offset)} {data}"
                await self.publish(
                    "mc.post",
                    cmd,
                )

        #### FENCES
        fence = mc.Block("stone_brick_wall")
        await self.publish("mc.post", f"setblock {sign_start.offset(y=-1)} {fence}")
        await self.publish("mc.post", f"setblock {sign_start.offset(y=-2)} {fence}")
        await self.publish(
            "mc.post",
            f"setblock {sign_start.offset(x = self.config.podium_size + 1, y=-1)} {fence}",
        )
        await self.publish(
            "mc.post",
            f"setblock {sign_start.offset(x = self.config.podium_size + 1, y=-2)} {fence}",
        )

        #### BENCH
        bench_start = origin.offset(x=-self.config.podium_size, y=-4, z=-1)
        bench_block = mc.Block("stripped_oak_wood")
        bench_block.blockstate = mc.BlockState({"axis": "x"})

        await self.publish(
            "mc.post",
            f"fill {bench_start} {bench_start.offset(x = self.config.podium_size * 2)} {bench_block}",
        )

        #### GRASS
        grass_start = origin.offset(x=-self.config.podium_size, y=-5)
        grass_block = mc.Block("grass_block")

        await self.publish(
            "mc.post",
            f"fill {grass_start} {grass_start.offset(x = self.config.podium_size * 2)} {grass_block}",
        )

    async def reset_podium(self):
        await self.remove_all_npc()
        await self.reset_signs()
        await self.publish("mc.post", "kill @e[type=minecraft:block_display]")

    async def reload_podium(self):
        await self.reset_podium()
        await self.remove_podium()
        await self.reload_config()
        await self.build_podium()


if __name__ == "__main__":
    action = Podium()
    while True:
        try:
            asyncio.run(action.run())
        except Exception as e:
            error_msg = f"An error occurred: {e}"
            print(error_msg)
            print("-> Restarting in 1 seconds...")
            time.sleep(1)
