import asyncio
import math
from dill import dumps

import shulker as mc
from tools.config import config
from tools.pulsar import Portal


def get_sign_data(messages, pos):
    top_colors = ["yellow", "white", "gold", "black", "black"]

    a = f"""{{front_text:{{color:"white",has_glowing_text:1b,messages:['{{"text":"{messages[0]}", "color":"{top_colors[pos - 1]}"}}','{{"text":"{messages[1]}", "color":"{top_colors[pos - 1]}"}}','{{"text":"{messages[2]}", "color":"{top_colors[pos - 1]}"}}','{{"text":"{messages[3]}", "color":"{top_colors[pos - 1]}"}}']}}}} """
    return a


def coords_from_pos(start, pos):
    # this code breaks for config.podium_size > 5
    # https://discord.com/channels/@me/678579998847926273/1150958377745256578
    if config.podium_size > 5:
        raise ValueError("config.podium_size > 5 not supported")

    pitch_delta = [-10, -5, 0, 5, 10]
    coords = mc.Coordinates(start.x, start.y, start.z, yaw=-30, pitch=pitch_delta[pos])
    deltas = [-1.85, -0.7, 0.5, 1.7, 2.85]

    return coords.offset(x=deltas[pos]), coords.yaw, coords.pitch


class Podium(Portal):
    async def on_join(self):
        await self.subscribe("gl.spawn_winner", self.spawn_winner)
        await self.subscribe("gl.reset_podium", self.reset_podium)
        await self.subscribe("gl.rebuild_podium", self.rebuild_podium)
        await self.reset_podium()

    async def spawn_winner(self, args):
        def spawn_npc(name, pos, podium_pos):
            cmd = f'sudo {config.camera_name} /npc create --at {pos[0].x}:{pos[0].y}:{pos[0].z} --nameplate true "+{config.scores_template[podium_pos - 1]}"'
            mc.post(cmd)

            mc.post(
                f"sudo {config.camera_name} /npc moveto --pitch {pos[1]} --yaw {pos[2]}"
            )

            mc.post(f"sudo {config.camera_name} /npc skin -s {name}")

        pos, name, score = args
        if pos > config.podium_size:
            cmd = f'title {config.camera_name} actionbar {{"text":"{name} found the word #{pos}"}}'
            await self.publish("mc.post", cmd)
            return

        print("spawn winner", pos, name, score)
        spawn_start = config.podium_pos.offset(y=-3, z=-0.2)
        coords = coords_from_pos(spawn_start, pos - 1)

        f = lambda: spawn_npc(name, coords, pos)
        await self.publish("mc.lambda", dumps(f))

        cmd = f"particle wax_on {coords[0]} 0 0 0 6 100 normal"
        print(cmd)
        await self.publish("mc.post", cmd)
        cmd = f"particle wax_off {coords[0]} 0 0 0 6 100 normal"
        print(cmd)
        await self.publish("mc.post", cmd)

        sign_start = config.podium_pos.offset(x=math.floor(-config.podium_size / 2))
        sign_message = [
            f"#{pos}",
            "",
            f"{name}",
            f"{score} pts",
        ]

        data = get_sign_data(sign_message, pos)

        await self.publish(
            "mc.post", f"data merge block {sign_start.offset(x=pos)} {data}"
        )

        cmd = f'title {config.camera_name} actionbar {{"text":"{name} found the word #{pos}"}}'
        print(cmd)
        await self.publish("mc.post", cmd)

    async def remove_podium(self):
        origin = config.podium_pos
        pos1 = origin.offset(x=-10, y=-10, z=-10)
        pos2 = origin.offset(x=10, y=10, z=10)
        zone = mc.BlockZone(pos1, pos2)
        cmd = f"fill {zone} air"
        await self.publish("mc.post", cmd)

    async def remove_all_npc(self):
        cmd = f"npc remove all"
        await self.publish("mc.post", cmd)

    async def reset_signs(self):
        sign_start = config.podium_pos.offset(x=math.floor(-config.podium_size / 2))
        for x_offset, _ in enumerate(range(config.podium_size + 1)):
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
        origin = config.podium_pos

        ###### SIGN LINE
        sign_line = []

        # front_text:{color:"orange",,}
        # /setblock 16 133 57 minecraft:oak_wall_hanging_sign[facing=south,waterlogged=false]{,is_waxed:0b}
        wood = mc.Block("oak_wood")
        sign = mc.Block("oak_wall_hanging_sign")
        sign.blockstate = mc.BlockState({"facing": "south"})

        sign_line.append(wood)
        for _ in range(config.podium_size):
            sign_line.append(sign)

        sign_line.append(wood)

        sign_start = origin.offset(x=math.floor(-config.podium_size / 2))
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
            f"setblock {sign_start.offset(x = config.podium_size + 1, y=-1)} {fence}",
        )
        await self.publish(
            "mc.post",
            f"setblock {sign_start.offset(x = config.podium_size + 1, y=-2)} {fence}",
        )

        #### BENCH
        bench_start = origin.offset(x=-config.podium_size, y=-4, z=-1)
        bench_block = mc.Block("stripped_oak_wood")
        bench_block.blockstate = mc.BlockState({"axis": "x"})

        await self.publish(
            "mc.post",
            f"fill {bench_start} {bench_start.offset(x = config.podium_size * 2)} {bench_block}",
        )

        #### GRASS
        grass_start = origin.offset(x=-config.podium_size, y=-5)
        grass_block = mc.Block("grass_block")

        await self.publish(
            "mc.post",
            f"fill {grass_start} {grass_start.offset(x = config.podium_size * 2)} {grass_block}",
        )

        ### BACKGROUND
        background_start = origin.offset(x=-config.podium_size * 2, y=-5, z=-9)
        background_block = mc.Block("end_portal")
        await self.publish(
            "mc.post",
            f"fill {background_start} {background_start.offset(x = config.podium_size * 4, z=7)} {background_block}",
        )

        barrier_block = mc.Block("barrier")
        await self.publish(
            "mc.post",
            f"fill {background_start.offset(y=1)} {background_start.offset(x = config.podium_size * 4, y=1, z=7)} {barrier_block}",
        )

    async def reset_podium(self):
        await self.remove_all_npc()
        await self.reset_signs()

    async def rebuild_podium(self):
        await self.reset_podium()
        await self.remove_podium()
        await self.build_podium()


if __name__ == "__main__":
    action = Podium()
    asyncio.run(action.run())
