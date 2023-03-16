import asyncio

from tools.config import config
from tools.database import db
from tools.pulsar import PulsarWrapper


async def main():
    async with PulsarWrapper() as pulsar:
        
    
if __name__ == "__main__":
    print(f"-> Starting {__file__.split('/')[-1]}")
    asyncio.run(main())
    print(f"-> {__file__.split('/')[-1]} is stopping")