import asyncio
import aiopulsar
import pulsar
import json
import uuid
import os
import logging as log

from pulsar import AuthenticationToken
from dotenv import load_dotenv

load_dotenv()

PULSAR_URL = os.getenv("PULSAR_URL")
PULSAR_TOKEN = os.getenv("PULSAR_TOKEN")
PULSAR_NAMESPACE = os.getenv("PULSAR_NAMESPACE")
prefix = f'non-persistent://{PULSAR_NAMESPACE}/'

pulsar_logger = log.getLogger("pulsar")
pulsar_logger.setLevel(log.CRITICAL)

class PulsarWrapper:
    def __init__(self, verbose=False):
        self.client = None
        self.subscription_ready_events = {}
        self.subscribe_tasks = []
        self.registered_functions = {}
        self.verbose = verbose

    async def __aenter__(self):
        self.client = await aiopulsar.connect(PULSAR_URL, authentication=AuthenticationToken(PULSAR_TOKEN), logger=pulsar_logger)
        print("-> Pulsar connection established")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        for task in self.subscribe_tasks:
            task.cancel()
            await task
            
        await self.client.close()
        print("-> Pulsar connection closed")
        
    async def register(self, topic_name, func):
        if self.verbose:
            print(f"-> Registering function {topic_name} for func: {func}")
            
        self.registered_functions[topic_name] = func
        await self.subscribe(topic_name, self._registered_function_callback)

    async def _registered_function_callback(self, message):
        request = json.loads(message)
        function_name = request['function']
        args = request['args']
        kwargs = request['kwargs']

        func = self.registered_functions.get(function_name)
        if func:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            response_topic = request['response_topic']
            await self.publish(response_topic, json.dumps(result))

    async def call(self, function_name, *args, **kwargs):
        if self.verbose:
            print(f"-> Calling function {function_name}")
            
        response_topic = f'response-{function_name}-{uuid.uuid4()}'
        request = {
            'function': function_name,
            'args': args,
            'kwargs': kwargs,
            'response_topic': response_topic
        }
        await self.publish(function_name, json.dumps(request))

        future = asyncio.get_event_loop().create_future()

        async def handle_response(message):
            future.set_result(json.loads(message))

        await self.subscribe(response_topic, handle_response)
        result = await future
        return result
      
    async def publish(self, topic, message):
        if self.verbose:
            print(f"-> Publishing to {topic} => {message}")
            
        async with self.client.create_producer(topic=prefix + topic) as producer:
            if isinstance(message, bytes):
                await producer.send(message)
            else:
                await producer.send(message.encode('utf-8'))

    async def subscribe(self, topic, callback):
        if self.verbose:
            print(f"-> Subscribing to {topic}, callback: {callback}")
            
        if topic not in self.subscription_ready_events:
              self.subscription_ready_events[topic] = asyncio.Event()
              
        self.subscription_ready_events[topic].clear()
        task = asyncio.create_task(self._subscribe(topic, callback))
        self.subscribe_tasks.append(task)
        await self.subscription_ready_events[topic].wait()
        return task
      
    async def _subscribe(self, topic, callback):
        async with self.client.subscribe(
            topic=prefix + topic,
            subscription_name='my-subscription',
            consumer_name="my-consumer",
            initial_position=pulsar.InitialPosition.Earliest
        ) as consumer:
            self.subscription_ready_events[topic].set()
            while True:
                try:
                    msg = await consumer.receive()
                    data = msg.data().decode('utf-8')
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                    await consumer.acknowledge(msg)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    print(f"An error occurred while processing the message: {e}")

            await asyncio.sleep(0.01)
            
    async def close(self):
        await self.client.close()