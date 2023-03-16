import asyncio
import datetime

from dill import dumps
from TikTokLive.types.errors import FailedFetchRoomInfo
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import DisconnectEvent, ConnectEvent

from tools.config import config
from tools.database import db
from tools.pulsar import PulsarWrapper
from tools.sanitize import get_profile

listeners = ["comment", "follow", "join", "share", "like", "gift"]
topic_prefix = "live."
# This means that the topic will be live.comment, live.follow, etc.

async def main():
    async with PulsarWrapper(verbose=False) as pulsar:
        client = connect(config.stream_id)
        
        for listener in listeners:
            # This will call the parse_and_publish function with the event and the listener, for each of them
            # when the tiktok event is triggered
            client.add_listener(listener, lambda event, listener=listener: parse_and_publish(pulsar, event, listener))
        
        # And this will call the views_handler function when the viewer_update event is triggered
        # Which stores the current amount of viewers in the stream as well as commit the database
        client.add_listener("viewer_update", lambda event: views_handler(event))
        
        task = asyncio.create_task(client._start())  # Create a task for the client's event loop

        await task
        
def connect(stream_id):
  """Connects to the streamer's room and sets up the connection handlers"""
  if stream_id == "": exit("No streamer id defined")
      
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

async def parse_and_publish(pulsar, event, listener: str):
    """Parse and publish events to the database and to pulsar"""
    if not event.user: return
    
    user = get_profile(event)
    
    try:
        await pulsar.publish(topic_prefix + listener, dumps(user))
        if config.verbose:
            print(f"Message was successfully delivered to live.{listener}")
    except Exception as e:
        if config.verbose:
            print(f"Message was not delivered to any consumer and has been discarded")
        print(e)

    db.add_new_user(user)
    db.add_event(user, listener)
    
    #if config.verbose:
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
    print(f"-> Starting {__file__.split('/')[-1]}")
    asyncio.run(main())
    print(f"-> {__file__.split('/')[-1]} is stopping")