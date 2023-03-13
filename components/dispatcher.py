import asyncio
import datetime
import time
import os

from dotenv import load_dotenv
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

from config import config, db
from components.tools.sanitize import get_profile


class Component(ApplicationSession):
    async def onJoin(self, details):
      
        if config.stream_id == "":
          exit("No streamer id defined")
        try:
            client = TikTokLiveClient(unique_id=f"@{config.stream_id}")
        except FailedFetchRoomInfo:
            print(f"Failed to connect to @{config.stream_id}")
            return

        def parse_and_publish(listener: str, event):
            if event.user:
                user = get_profile(event)
                self.publish(f"chat.{listener}", (user))
                db.add_new_user(user)
                db.add_event(user, listener)
                if config.verbose:
                    print(f"{datetime.datetime.now()} | {listener.upper()} | {event.user.nickname}")
            else:
                if config.verbose:
                    print(
                        f"[{listener.upper()}] Failed to get profile for {event.user.unique_id}"
                    )
        
        with open("viewer_count.txt", "a") as f:
            f.write(
                f"{datetime.datetime.now()} | Now parsing viewers for: @{config.stream_id}\n"
            )

        @client.on("connect")
        async def on_connect(_: ConnectEvent):
            print(f"Connected to @{config.stream_id} Room ID: [{client.room_id}]")

        @client.on("disconnect")
        async def on_disconnect(event: DisconnectEvent):
            loop = asyncio.get_running_loop()
            loop.create_task(client._connect())

        @client.on("comment")
        async def on_comment(event: CommentEvent):
            parse_and_publish("comment", event)

        @client.on("viewer_update")
        async def on_connect(event: ViewerUpdateEvent):
            db.store_views(event.viewer_count)
            db.commit()
            
            if config.verbose:
                print("--------------------------------------")
                print("Database commited, new viewer count: ", event.viewer_count)
                print("--------------------------------------")

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
    print(f"Starting Event dispatcher...")
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(Component)
