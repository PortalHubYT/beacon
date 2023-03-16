from dotenv import load_dotenv

load_dotenv()

config_values = {
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

config = Config()

