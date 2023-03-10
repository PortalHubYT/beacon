import asyncio
import datetime
import os
import json
import sys

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

from TikTokLive.types.errors import FailedFetchRoomInfo
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import (
    ViewerUpdateEvent,
    DisconnectEvent,
    CommentEvent,
    ConnectEvent,
    FollowEvent,
    LikeEvent,
    GiftEvent,
    JoinEvent,
    ShareEvent,
)

# Work around to be able to import from the same level folder 'tools'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.config import config, db
from tools.user_parsing import get_profile

streamer = config["stream_id"]
verbose = config["verbose"]


class Component(ApplicationSession):
    async def onJoin(self, details):
        try:
            client = TikTokLiveClient(unique_id=f"@{streamer}")
        except FailedFetchRoomInfo:
            print(f"Failed to connect to @{streamer}")
            return

        def parse_and_publish(handler: str, event):
            if event.user:
                user = get_profile(event)
                self.publish(f"chat.{handler}", (user))
            else:
                if verbose:
                    print(
                        f"[{handler.upper()}] Failed to get profile for {event.user.unique_id}"
                    )

        with open("viewer_count.txt", "a") as f:
            f.write(
                f"{datetime.datetime.now()} | Now parsing viewers for: @{streamer}\n"
            )

        @client.on("connect")
        async def on_connect(_: ConnectEvent):
            print(f"Connected to @{streamer} Room ID: [{client.room_id}]")

        @client.on("disconnect")
        async def on_disconnect(event: DisconnectEvent):
            loop = asyncio.get_running_loop()
            loop.create_task(client._connect())

        @client.on("comment")
        async def on_comment(event: CommentEvent):
            parse_and_publish("comment", event)

        @client.on("viewer_update")
        async def on_connect(event: ViewerUpdateEvent):
            with open("viewer_count.txt", "a") as f:
                f.write(f"{datetime.datetime.now()} | {event.viewer_count}\n")

        @client.on("follow")
        async def on_follow(event: FollowEvent):
            parse_and_publish("follow", event)

        @client.on("join")
        async def on_join(event: JoinEvent):
            parse_and_publish("join", event)

        @client.on("share")
        async def on_share(event: ShareEvent):
            parse_and_publish("share", event)

        @client.on("like")
        async def on_like(event: LikeEvent):
            parse_and_publish("like", event)

        @client.on("gift")
        async def on_gift(event: GiftEvent):
            parse_and_publish("gift", event)

        loop = asyncio.get_running_loop()
        loop.create_task(client._connect())


if __name__ == "__main__":
    print(f"Starting Parser...")
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(Component)
