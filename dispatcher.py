import asyncio
import datetime
import time
import os

from dotenv import load_dotenv
from pulsar import Client, AuthenticationToken
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

def connect():
  """
  Connects to the streamer's room and sets up the connection handlers
  """
  if config.stream_id == "":
      exit("No streamer id defined")
      
  try:
      client = TikTokLiveClient(unique_id=f"@{config.stream_id}")
 
  except FailedFetchRoomInfo:
      exit(f"Failed to connect to @{config.stream_id}")
      
  @client.on("connect")
  async def on_connect(event: ConnectEvent):
      print(f"Connected to @{config.stream_id} Room ID: [{client.room_id}]")

  @client.on("disconnect")
  async def on_disconnect(event: DisconnectEvent):
      client._connect()
    
  return client


async def parse_and_publish(event, listener: str):
    """
    Parse and publish events to the database
    """
    if not event.user: return
    
    user = get_profile(event)
    #TODO: 
    """self.publish(f"chat.{handler}", (user))"""

    db.add_new_user(user)
    db.add_event(user, listener)
    
    if config.verbose:
      print(f"{datetime.datetime.now()} | {listener.upper()} | {event.user.nickname}")
        
            
def views_handler(event):
  """
  Commits the new viewer count to the database.
  This also commits all the events that have been stored in the database.
  """
  
  db.store_views(event.viewer_count)
  db.commit()
  
  if config.verbose:
    print("--------------------------------------")
    print("Database commited, new viewer count: ", event.viewer_count)
    print("--------------------------------------")


if __name__ == "__main__":
    print(f"Starting Dispatcher...")
    client = connect()
    
    # TODO: Remove this in production!!!!
    db.reset_database()
    
    listeners = ["comment", "follow", "join", "share", "like", "gift"]

    for listener in listeners:
        client.add_listener(listener, lambda event, listener=listener: parse_and_publish(event, listener))
        
    client.add_listener("viewer_update", lambda event: views_handler(event))
    
    client.run()
