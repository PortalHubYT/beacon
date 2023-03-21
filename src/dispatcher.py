import asyncio
import datetime
import logging
import time

from TikTokLive.types.errors import FailedFetchRoomInfo
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import DisconnectEvent, ConnectEvent

from tools.config import config
from tools.database import db
from tools.sanitize import get_profile
from tools.pulsar import Portal

logging.basicConfig(
    filename='logs/dispatcher_error.log',
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

listeners = ["comment", "follow", "join", "share", "like", "gift"]
topic_prefix = "live."
# This means that the topic will be live.comment, live.follow, etc.

class Dispatch(Portal):
    async def loop(self):
        print("-> Connecting TikTok client")
        self.client = self.connect(config.stream_id)

        print("-> Adding all the listeners...")
        for listener in listeners:
            self.client.add_listener(listener, lambda event, listener=listener: self.parse_and_publish(event, listener))

        self.client.add_listener("viewer_update", lambda event: self.views_handler(event))
        print("-> Done!")
        
        print("-> Starting dispatcher...")
        try:
            await self.client._start()
        except Exception as e:
            error_msg = f"An error occurred: {e}"
            print(error_msg)
            logging.error(error_msg)
            
        print("-> Dispatcher stopped?")
        await asyncio.sleep(15)

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
            error_msg = f"An error occurred: {e}"
            print(error_msg)
            logging.error(error_msg)


        return client

    async def parse_and_publish(self, event, listener: str):
        if not event.user:
            return
                
        if listener not in config.listen_to: return

        user = get_profile(event)

        try:
            await self.publish(topic_prefix + listener, user)
        except Exception as e:
            if config.verbose:
                print(f"-> Message was not delivered to any consumer and has been discarded")
            print(e)

        db.add_new_user(user)
        db.add_event(user, listener)
        
        if config.verbose:
            print(f"{datetime.datetime.now()} | {listener.upper()} | {user['display']}")

    def views_handler(self, event):
        db.store_views(event.viewer_count)
        db.commit()

        if config.verbose:
            print("--------------------------------------")
            print("Database committed, new viewer count: ", event.viewer_count)
            print("--------------------------------------")

if __name__ == "__main__":
    dispatch = Dispatch()
    while True:
        try:
            asyncio.run(dispatch.run(), debug=True)
        except Exception as e:
            error_msg = f"An error occurred: {e}"
            print(error_msg)
            logging.error(error_msg)
            print("-> Restarting in 5 seconds...")
            time.sleep(5)
    