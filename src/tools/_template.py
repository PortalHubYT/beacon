import asyncio

from tools.config import config
from tools.database import db
from tools.pulsar import PulsarWrapper

# In this example, this function will be registered
# and also subscribed to
async def print_message(message):
    print(message)
    await asyncio.sleep(2)
    return message.upper()

# When using pulsar, we have to work within
# the context of an open pulsar connection, see line 18
# The functions are named and should work the same as crossbar
async def main():
    async with PulsarWrapper() as pulsar:
        
        # ------------- PUB/SUB -----------------
        
        await pulsar.subscribe("test", print_message)
        
        ret = await pulsar.publish("test", "Just published a message!")
        print(ret, end='\n-------------\n') # <- This will be None
        
        # --------------- RPC -------------------
        
        await pulsar.register("testina", print_message)
        
        ret = await pulsar.call("testina", "Just called a message!")
        print(ret) # <- This will be "JUST CALLED A MESSAGE!" after 2 seconds
    
if __name__ == "__main__":
    print(f"-> Starting {__file__.split('/')[-1]}")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    print(f"-> {__file__.split('/')[-1]} is stopping")