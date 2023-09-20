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
prefix = f"non-persistent://{PULSAR_NAMESPACE}/"

# Wraps the Hub to create an inheritable class that can be used
# as an open connection to pulsar and an async loop
class Portal:
    def __init__(self, sleep=0.0001):
        self.pulsar = None
        self.should_stop = False
        self.sleep = sleep

    async def setup(self):
        self.pulsar = Hub()
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

    async def register(self, topic_name, func):
        await self.pulsar.register(topic_name, func)

    async def subscribe(self, topic, callback, subscription_name=None):
        await self.pulsar.subscribe(topic, callback, subscription_name)

    async def publish(self, topic, message=None):
        await self.pulsar.publish(topic, message)

    async def call(self, function_name, *args, **kwargs):
        return await self.pulsar.call(function_name, *args, **kwargs)


# Wraps pulsar to create a pub/sub and RPC object
class Hub:
    def __init__(self, verbose=True):
        self.client = None
        self.verbose = verbose

        self.subscription_ready_events = {}
        self.subscribe_tasks = []

        self.registered_functions = {}
        self.pending_calls = {}

    async def __aenter__(self):
        
        pulsar_logger = log.getLogger("pulsar")
        pulsar_logger.setLevel(log.CRITICAL)

        self.client = await aiopulsar.connect(
            PULSAR_URL,
            authentication=AuthenticationToken(PULSAR_TOKEN),
            logger=pulsar_logger,
        )
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

    async def publish(self, topic, message):
        async with self.client.create_producer(topic=prefix + topic) as producer:
            await producer.send(pickle.dumps(message))

    async def subscribe(self, topic, callback, subscription_name=None):
        if subscription_name is None:
            subscription_name = topic + "-subscription" + str(uuid.uuid4())

        if topic not in self.subscription_ready_events:
            self.subscription_ready_events[topic] = asyncio.Event()

        self.subscription_ready_events[topic].clear()
        task = asyncio.create_task(self._subscribe(topic, callback, subscription_name))
        self.subscribe_tasks.append(task)
        await self.subscription_ready_events[topic].wait()
        return task

    async def _subscribe(self, topic, callback, subscription_name):
        async with self.client.subscribe(
            topic=prefix + topic,
            subscription_name=subscription_name,
            consumer_name=topic + "-consumer",
            initial_position=pulsar.InitialPosition.Earliest,
        ) as consumer:
            self.subscription_ready_events[topic].set()

            while True:
                try:
                    msg = await consumer.receive()
                    data = pickle.loads(msg.data())

                    if (
                        type(data) is dict
                        and data.get("type")
                        and data["type"] == "request"
                    ):
                        if topic in self.registered_functions:
                            result = self.registered_functions[topic](
                                *data["args"], **data["kwargs"]
                            )

                            response_message = {
                                "type": "response",
                                "request_id": data["request_id"],
                                "result": result,
                            }
                            await self.publish(topic + "_response", response_message)

                        else:
                            print(f"Topic '{topic}' not registered.")

                    else:
                        if asyncio.iscoroutinefunction(callback):
                            if data == None:
                                await callback()
                            else:
                                await callback(data)
                        else:
                            if data == None:
                                callback()
                            else:
                                callback(data)

                    await consumer.acknowledge(msg)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    print(f"An error occurred while processing the message:")
                    traceback.print_exc()

            await asyncio.sleep(0.001)

    async def register(self, topic_name, function):
        self.registered_functions[topic_name] = function

    async def call(self, topic, *args, **kwargs):
        request_id = str(uuid.uuid4())
        request_message = {
            "type": "request",
            "request_id": request_id,
            "args": args,
            "kwargs": kwargs,
        }
        response_future = asyncio.Future()

        # Subscribe to the response topic if not already subscribed
        if topic + "_response" not in self.subscription_ready_events:
            await self.subscribe(topic + "_response", self._handle_response)

        self.pending_calls[request_id] = response_future
        await self.publish(topic, request_message)

        return await response_future

    async def _handle_response(self, data):
        if "request_id" in data and "result" in data:
            request_id = data["request_id"]
            if request_id in self.pending_calls:
                self.pending_calls[request_id].set_result(data["result"])
                del self.pending_calls[request_id]
