import os

from dotenv import load_dotenv
load_dotenv()

config_values = {
    "server_ip": os.getenv("MINECRAFT_IP"),
    "rcon_port": os.getenv("MINECRAFT_RCON_PORT"),
    "rcon_password": os.getenv("MINECRAFT_RCON_PASSWORD"),
    "stream_ready": True,
    "stream_id": "tv_asahi_news",
    "verbose": False,
    "crop_size": 50
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

