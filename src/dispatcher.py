import asyncio
import datetime
import logging
import os
import time

from TikTokLive import TikTokLiveClient
from TikTokLive.types.errors import FailedFetchRoomInfo
from TikTokLive.types.events import ConnectEvent, DisconnectEvent

from tools.config import config
from tools.pulsar import Portal
from tools.sanitize import get_profile

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

listeners = ["comment", "follow", "join", "share", "like", "gift"]
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

        self.client.add_listener(
            "viewer_update", lambda event: self.views_handler(event)
        )
        print("-> Done!")

        print("-> Starting dispatcher...")
        try:
            await self.client.start()
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise e
            error_msg = f"An error occurred: {e}"
            print(error_msg)
            logging.error(error_msg)


    def connect(self, stream_id):
        if stream_id == "":
            exit("-> No streamer id defined")
            
        try:
            print(f"-> Trying to connect to @{stream_id}...")
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
            exit("-> Exiting...")

        return client

    async def parse_and_publish(self, event, listener: str):
        if not event.user:
            return

        if listener not in config.listen_to:
            return
        
        if listener == "gift" and event.gift.info.type == 1 and event.gift.is_repeating == 1:
            return

        start = time.time()
        
        try:
            user = get_profile(event)
        except:
            print(f"-> Failed to parse {event}")
            return

        # await self.publish("db", ("add_new_user", user))
        # await self.publish("db", ("add_event", user, listener))
        
        try:
            await self.publish(topic_prefix + listener, user)
        except Exception as e:
            if config.verbose:
                print(
                    f"-> Message was not delivered to any consumer and has been discarded"
                )
            print(e)

        if config.verbose:
            print(f"{datetime.datetime.now().strftime('%H:%M:%S')} (took {time.time() - start:.2f}) | {listener.upper().ljust(7)} | {user['display']}")

    async def views_handler(self, event):
        await self.publish("db", ("store_views", event.viewer_count))
        await self.publish("db", ("commit",))
        await self.publish("live.viewer_update", event.viewer_count)
        
        if config.verbose:
            print("--------------------------------------")
            print("Database committed, new viewer count: ", event.viewer_count)
            print("--------------------------------------")


if __name__ == "__main__":
    # We check if there's an arg, if there is one, it overrides the config.stream_id
    import sys
    if len(sys.argv) > 1:
        config.stream_id = sys.argv[1]
    
    dispatch = Dispatch()
    while True:
        try:
            asyncio.run(dispatch.run(), debug=True)
        except Exception as e:
            # get full stacktrace
            import traceback
            traceback.print_exc()
            error_msg = f"An error occurred: {e}"
            print(error_msg)
            logging.error(error_msg)
            print("-> Restarting in 5 seconds...")
            time.sleep(5)
