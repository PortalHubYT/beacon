import asyncio
import datetime
import logging
import time
import os

from TikTokLive.types.errors import FailedFetchRoomInfo
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import DisconnectEvent, ConnectEvent

from tools.config import config
from tools.sanitize import get_profile
from tools.pulsar import Portal

# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)

# Get the directory containing the current file
directory = os.path.dirname(current_file_path)

# Construct the absolute file path by joining the directory and the desired file name
log_file_path = os.path.join(directory, "tools/logs/dispatcher_error.log")

os.mkdir(os.path.join(directory, "tools/logs/")) if not os.path.exists(
    os.path.join(directory, "tools/logs/")
) else None
# open(log_file_path, "w+")

logging.basicConfig(
    filename=log_file_path,
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

listeners = ["comment", "gift"]
topic_prefix = "live."
# This means that the topic will be live.comment, live.follow, etc.


class Dispatch(Portal):
    async def on_join(self):
        self.client = self.connect(config.stream_id)
        self.word = None

        print("-> Adding all the listeners...")
        for listener in listeners:
            self.client.add_listener(
                listener,
                lambda event, listener=listener: self.parse_and_publish(
                    event, listener
                ),
            )

        await self.subscribe("gl.new_word", self.new_word)
        await self.publish("dispatcher.get_word")

        print("-> Starting dispatcher...")
        loop = asyncio.get_running_loop()
        loop.create_task(self.client._connect())

    def connect(self, stream_id):
        if stream_id == "":
            exit("-> No streamer id defined")

        try:
            client = TikTokLiveClient(unique_id=f"@{stream_id}")
        except FailedFetchRoomInfo:
            exit(f"-> Failed to connect to @{stream_id}")

        @client.on("connect")
        async def on_connect(event: ConnectEvent):
            print(f"-> Connected to @{stream_id} Room ID: [{client.room_id}]")

        @client.on("disconnect")
        async def on_disconnect(event: DisconnectEvent):
            print(f"-> Disconnected from @{stream_id} Room ID: [{client.room_id}]")
            print(f"-> Trying to reconnect...")
            client._connect()

        @client.on("error")
        async def on_error(event):
            error_msg = f"(in dispatcher.py) An error occurred: {event}"
            print(error_msg)
            logging.error(error_msg)

        return client

    async def new_word(self, word):
        self.word = word
        print("-> New word:", self.word)

    async def parse_and_publish(self, event, listener: str):
        if not event.user or not self.word:
            print("no user or no word", event.user, self.word)
            print("too early for parse_and_pulish")
            return

        user = get_profile(event)
        print("comment")
        guess = user["comment"].strip().lower()
        if guess == self.word and listener == "comment":
            print("comment is good")
            await self.publish("db", ("add_new_user", user))
            await self.publish("db", ("commit",))

            await self.publish(topic_prefix + "win", user)
        elif listener == "gift":
            await self.publish(topic_prefix + listener, user)

        print("event:", listener)
        await self.publish("dispatcher.alive")

        if config.verbose and listener != "join":
            print(f"{datetime.datetime.now()} | {listener.upper()} | {user['display']}")


if __name__ == "__main__":
    dispatch = Dispatch()
    asyncio.run(dispatch.run(), debug=True)
