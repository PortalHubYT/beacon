import asyncio
import datetime

from TikTokLive.types.errors import FailedFetchRoomInfo
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import DisconnectEvent, ConnectEvent

from tools.config import config
from tools.database import db
from tools.sanitize import get_profile
from tools._base_action import BaseAction

listeners = ["comment", "follow", "join", "share", "like", "gift"]
topic_prefix = "live."
# This means that the topic will be live.comment, live.follow, etc.

class Dispatch(BaseAction):
    async def on_join(self):
        self.client = self.connect(config.stream_id)

        for listener in listeners:
            self.client.add_listener(listener, lambda event, listener=listener: self.parse_and_publish(event, listener))

        self.client.add_listener("viewer_update", lambda event: self.views_handler(event))
        
        await self.client._start()

    def connect(self, stream_id):
        if stream_id == "":
            exit("No streamer id defined")

        try:
            client = TikTokLiveClient(unique_id=f"@{stream_id}")
        except FailedFetchRoomInfo:
            exit(f"Failed to connect to @{stream_id}")

        @client.on("connect")
        async def on_connect(event: ConnectEvent):
            print(f"Connected to @{stream_id} Room ID: [{client.room_id}]")

        @client.on("disconnect")
        async def on_disconnect(event: DisconnectEvent):
            client._connect()

        return client

    async def parse_and_publish(self, event, listener: str):
        if not event.user:
            return

        user = get_profile(event)

        try:
            await self.publish(topic_prefix + listener, user)
            if config.verbose:
                print(f"Message was successfully delivered to live.{listener}")
        except Exception as e:
            if config.verbose:
                print(f"Message was not delivered to any consumer and has been discarded")
            print(e)

        db.add_new_user(user)
        db.add_event(user, listener)

        print(f"{datetime.datetime.now()} | {listener.upper()} | {event.user.nickname}")

    def views_handler(self, event):
        db.store_views(event.viewer_count)
        db.commit()

        if config.verbose:
            print("--------------------------------------")
            print("Database committed, new viewer count: ", event.viewer_count)
            print("--------------------------------------")

if __name__ == "__main__":
    dispatch = Dispatch()
    asyncio.run(dispatch.run())
