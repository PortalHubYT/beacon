import asyncio
import aiopulsar
import pulsar
import json
import uuid
import os
import logging as log
import signal
import traceback
import pickle
import datetime

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
        
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(signal.SIGINT, self.handle_signal)
        
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.graceful_exit()
        
    async def graceful_exit(self):
        print("-> Killing all pulsar subscriptions")
        for task in self.subscribe_tasks:
            task.cancel()
            await task
            
        await self.client.close()
        print("-> Pulsar connection closed")
        
    def handle_signal(self):
        print("-> Signal received, closing Pulsar connection.")
        loop = asyncio.get_event_loop()
        loop.remove_signal_handler(signal.SIGINT)
        loop.create_task(self.graceful_exit())
        exit(0)
        
    async def register(self, topic_name, func, subscription_name=None):
        if self.verbose:
            print(f"-> Registering function {topic_name} for func: {func}")
            
        self.registered_functions[topic_name] = func
        await self.subscribe(topic_name, self._registered_function_callback, subscription_name=subscription_name)

    async def _registered_function_callback(self, message):
        print("Registered function callback")
        if type(message) != bytes:
            return
        
        request = pickle.loads(message)
        
        if self.verbose:
            print(f"{datetime.datetime.now()} -> Got message for registered function: {message}")

        if not request.get('is_call'):
            return
        
        topic = request['topic']
        args = request['args']
        kwargs = request['kwargs']

        func = self.registered_functions.get(topic)
        if func:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            response_topic = request['response_topic']
            await self.publish(response_topic, pickle.dumps(result))

    async def call(self, topic, *args, **kwargs):
        print("Call " + topic)
        if self.verbose:
            print(f"{datetime.datetime.now()} -> Calling function {topic}")
            
        response_topic = f'response-{topic}-{uuid.uuid4()}'
        request = {
            'topic': topic,
            'args': args,
            'kwargs': kwargs,
            'response_topic': response_topic,
            'is_call': True,
        }

        future = asyncio.get_event_loop().create_future()

        async def handle_response(message):
            future.set_result(pickle.loads(message))

        await self.subscribe(response_topic, handle_response)
        
        await self.publish(topic, pickle.dumps(request))
        
        result = await future
        if self.verbose:
            print(f"{datetime.datetime.now()} -> Got response for {topic}: [{result}]")
        return result
      
    async def publish(self, topic, message):
        print("Publish")
        if self.verbose:
            print(f"{datetime.datetime.now()} -> Publishing to {topic} => {message}")
            
        async with self.client.create_producer(topic=prefix + topic) as producer:
            await producer.send(pickle.dumps(message))

    async def subscribe(self, topic, callback, subscription_name=None):
        if self.verbose:
            print(f"{datetime.datetime.now()} -> Subscribing to {topic}, callback: {callback}")
        
        if subscription_name is None:
            subscription_name = topic + '-subscription'
            
        if topic not in self.subscription_ready_events:
              self.subscription_ready_events[topic] = asyncio.Event()
              
        self.subscription_ready_events[topic].clear()
        task = asyncio.create_task(self._subscribe(topic, callback, subscription_name))
        self.subscribe_tasks.append(task)
        await self.subscription_ready_events[topic].wait()
        return task
      
    async def _subscribe(self, topic, callback, subscription_name):
        print("Subscribe")
        async with self.client.subscribe(
            topic=prefix + topic,
            subscription_name=subscription_name,
            consumer_name=topic + "-consumer",
            initial_position=pulsar.InitialPosition.Earliest
        ) as consumer:
            self.subscription_ready_events[topic].set()
            while True:
                try:
                    msg = await consumer.receive()
                    data = pickle.loads(msg.data())
                    
                    if self.verbose:
                        print(f"{datetime.datetime.now()} -> Received message from {topic}: {data}")
                        
                    if type(data) == dict:
                        if data.get('is_call', False):
                            continue
                    
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                    await consumer.acknowledge(msg)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    print(f"An error occurred while processing the message:")
                    traceback.print_exc()

            await asyncio.sleep(0.01)
            
    async def close(self):
        await self.client.close()