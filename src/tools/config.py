import os

import shulker as mc
from dotenv import load_dotenv
load_dotenv()

config_values = {
    "server_ip": os.getenv("MINECRAFT_IP"),
    "rcon_port": os.getenv("MINECRAFT_RCON_PORT"),
    "rcon_password": os.getenv("MINECRAFT_RCON_PASSWORD"),
    "stream_ready": True,
    "stream_id": "tv_asahi_news",
    "verbose": True,
    "listen_to": ["comment", "follow", "join", "share", "like", "gift"],
    "crop_size": 50,
    "camera_name": "PortalHub",
    "round_time": 30,
    "camera_pos": mc.Coordinates(0, 100, 0, 180, 0),
    "hint_distance": 40,
    "hint_height": 20,
    "letters_to_reveal_in_percentage": 50,
    "drawing_finished_at_percentage": 90,
    "bench_size": 10,
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

