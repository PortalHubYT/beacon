import os

import shulker as mc
from dotenv import load_dotenv

load_dotenv()

config_values = {
    # ENV #####################
    "server_ip": os.getenv("MINECRAFT_IP"),
    "rcon_port": os.getenv("MINECRAFT_RCON_PORT"),
    "rcon_password": os.getenv("MINECRAFT_RCON_PASSWORD"),
    "stream_ready": True,
    "listen_to": ["comment", "gift", "follow", "like", "gift"],
    "stream_id": "portalhub",
    "verbose": True,
    "crop_size": 50,
    # METAGAME #####################
    "camera_name": "funyrom",
    "camera_pos": mc.Coordinates(0, 69, 30, 180, 0),
    "round_time": 60,
    "anomaly_odds_percentage": 10,
    # INFOBAR #####################
    "infobar_default": {
        "shown": True,
        "text": "You can see your rank and your character when you gift!",
        "color": "gold",
    },
    # PAINTER #####################
    "paint_start": mc.BlockCoordinates(-50, 43, -130),
    "keep_layering": True,
    "drawing_finished_at_percentage": 80,
    "width": 100,
    "height": 100,
    "paint_chunk_size": 10,
    "backboard_extra_size": 2,
    "backboard_extra_height": 20,
    "backboard_border_thickness": 3,
    "particle_data": {
        "name": "minecraft:dust",
        "delta": mc.Coordinates(0.2, 0.2, 0),
        "size": 1,
        "speed": 0.1,
        "amount": 10,
        "offset_to_block": {"x": 0, "y": 0, "z": 2},
    },
    # PODIUM #####################
    "podium_pos": mc.BlockCoordinates(0, 68, 23),
    "podium_size": 5,
    "scores_template": [10, 5, 3, 1, 1],
    "winstreak_minimum_viewers": 50,
    # HINT #####################
    "hint_palette": "stone",
    "word_len_limit": 13,
    "hint_start": mc.BlockCoordinates(0, 107, -45),
    "letters_to_reveal_in_percentage": 50,
    # MATCH #####################
    "round_per_match": 10,
    # GIFTS #####################
    "fake_gift_rate_seconds": 30,
    "gift_spacing_seconds": 4,
    "gift_drawing_trigger": 10,
    "npc_walk_speed": 0.5,
    "gifters_name_styling": "random",
    "gifter_message": "&lThanks for the gift! <3",
    # TIMER #####################
    "timer_start": mc.BlockCoordinates(-55, 175, -132),
    "timer_palette": [
        "black_concrete",
        "black_concrete",
        "gray_concrete",
        "gray_concrete",
        "white_concrete",
        "white_concrete",
        "gray_concrete",
        "gray_concrete",
    ],
    "timer_border_thickness": 2,
    "timer_height": 10,
}

config_values["banned_words"] = [
    "alien",
    "penguin",
    "snowflake",
    "pigeon",
    "hand grenade",
    "worm",
    "banana",
    "pinwheel",
    "dump truck",
    "beaver",
    "elephant",
    "mushroom",
    "milk tank" "dinosaur",
    "pig",
    "torpedo",
    "whale",
    "mushroom",
    "cow",
    "uterus",
    "banana",
    "witch",
    "cutter",
    "cones",
    "zombie",
    "testicle",
    "vagina",
    "penis",
    "breast",
    "clown",
    "crackers",
    "screwdriver",
    "rubbish",
    "jewelery",
    "buttocks",
    "catfish",
    "cat fish",
    "sack",
    "dog",
    "garbage",
    "socks",
    "pig",
    "gorilla",
    "cow",
    "monkey",
    "banana",
    "penis",
    "donkey",
    "joint",
    "hamburguer",
    "hippo",
    "rat",
    "testicles",
    "pinwheel",
    "beach",
    "grooming",
    "sloth",
    "walrus",
    "prawn",
    "stand",
    "underwear",
    "balloon",
]

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
