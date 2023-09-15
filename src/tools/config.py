import os

import shulker as mc
from dotenv import load_dotenv

load_dotenv()

config_values = {
    "server_ip": os.getenv("MINECRAFT_IP"),
    "rcon_port": os.getenv("MINECRAFT_RCON_PORT"),
    "rcon_password": os.getenv("MINECRAFT_RCON_PASSWORD"),
    "stream_ready": True,
    "listen_to": ["comment", "follow", "join", "share", "like", "gift"],
    "stream_id": "portalhub",
    "verbose": True,
    "crop_size": 50,
    "camera_name": "funyrom",
    "round_time": 45,
    "camera_pos": mc.Coordinates(0, 135, 30, 180, 20),
    "paint_start": mc.BlockCoordinates(-50, 60, -130),
    "drawing_finished_at_percentage": 80,
    "width": 100,
    "height": 100,
    "paint_chunk_size": 100,
    "hint_start": mc.BlockCoordinates(0, 150, -40),
    "hint_distance": 70,
    "hint_height": 10,
    "letters_to_reveal_in_percentage": 30,
    "podium_pos": mc.BlockCoordinates(0, 133, 25),
    "podium_size": 5,
    "scores_template": [10, 5, 3, 1, 1],
    "gift_trigger": 10,
    "hint_palette": "quartz",
}


class Config:
    def __init__(self):
        for key, value in config_values.items():
            setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)


# Config can be accessed both as:
# config["stream_ready"]
# config.stream_ready
config = Config()
