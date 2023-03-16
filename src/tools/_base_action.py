import asyncio

from tools.pulsar import PulsarWrapper

class BaseAction():
    def __init__(self, sleep=0.0001):
        self.pulsar = None
        self.should_stop = False
        self.sleep = sleep

    async def setup(self):
        self.pulsar = PulsarWrapper()
        await self.pulsar.__aenter__()

    async def teardown(self):
        if self.pulsar is not None:
            await self.pulsar.__aexit__(None, None, None)

    async def loop(self):
        pass
    
    async def execute(self):
        while not self.should_stop:
            await self.loop()
            await asyncio.sleep(self.sleep) 
            
    async def on_join(self):
        pass
    
    async def run(self):
        print(f"-> Starting {self.__class__.__name__}")
        try:
            await self.setup()
            await self.on_join()
            await self.execute()
        except KeyboardInterrupt:
            self.should_stop = True
        finally:
            await self.teardown()
        print(f"-> {self.__class__.__name__} is stopping")
    
    async def register(self, topic_name, func, subscription_name=None):
        await self.pulsar.register(topic_name, func, subscription_name)
        
    async def subscribe(self, topic, callback, subscription_name=None):
        await self.pulsar.subscribe(topic, callback, subscription_name)
        
    async def publish(self, topic, message):
        await self.pulsar.publish(topic, message)
        
    async def call(self, function_name, *args, **kwargs):
        return await self.pulsar.call(function_name, *args, **kwargs)
