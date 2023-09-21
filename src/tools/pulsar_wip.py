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

PULSAR_URL = "pulsar://localhost:6650"
PULSAR_TOKEN = os.getenv("PULSAR_TOKEN")
PULSAR_NAMESPACE = "public/default"
prefix = f"non-persistent://{PULSAR_NAMESPACE}/"

# Wraps the Hub to create an inheritable class that can be used
# as an open connection to pulsar and an async loop
class Portal:
    def __new__(cls, delay_between_restarts=0, max_restarts=0, stack_trace_amount=1,
                blocking=False, verbose=True, retro_compatibility=True):
        """
        This method is called before __init__.
        It lets us call the object like this: Portal(args)
        """
        
        portal = super().__new__(cls)
        portal.__init__(delay_between_restarts=delay_between_restarts,
                        max_restarts=max_restarts,
                        stack_trace_amount=stack_trace_amount,
                        blocking=blocking,
                        verbose=verbose,
                        retro_compatibility=retro_compatibility)

        if retro_compatibility:
            return portal
        
        try:
            asyncio.run(portal.open())
        except KeyboardInterrupt:
            print(f"-> Keyboard interrupt received. Exiting.")
    
    def __init__(self, delay_between_restarts=0, max_restarts=0, stack_trace_amount=1,
                 blocking=False, retro_compatibility=True):
        
        self.delay_between_restarts = delay_between_restarts
        self.max_restarts = max_restarts
        self.stack_trace_amount = stack_trace_amount
        self.restart_count = 0
        self.blocking = blocking
        self.tasks = set()
        
    async def open(self):
        should_continue = True
        
        while should_continue:
            self.tasks = set()
            
            try:
                self.hub = Hub()
                await self.hub.connect()
                print("-> Pulsar connection established")
                
                print(f"-> Processing {self.__class__.__name__}'s on join.")
                await self.on_join()
                
                self.tasks.update(self.hub.subscribe_tasks)  # Include Hub's subscribe_tasks
                print(f"-> {len(self.tasks)} tasks were set for {self.__class__.__name__}.")
                
                if self.blocking or self.hub.registered_functions:  # Only add loop task if there are other tasks
                    self.tasks.add(asyncio.create_task(self.loop()))
                
                # If no tasks are running, then exit
                if not self.tasks:
                    should_continue = False
                    print(f"-> No tasks were set, and blocking is set to False")
                    break
                
                if self.blocking and len(self.tasks) == 1:
                    print(f"-> Blocking is set to True, Will run until first exception.")
                else:
                    print(f"-> Starting {len(self.tasks)} tasks for {self.__class__.__name__}. Will run until first exception.")
                    
                done, pending = await asyncio.wait(self.tasks, return_when=asyncio.FIRST_EXCEPTION)
                
                for task in done:
                    if task.exception():
                        should_continue = await self.handle_exception(task.exception())
                        if not should_continue:
                            break

            except Exception as e:
                should_continue = await self.handle_exception(e)
            except (KeyboardInterrupt, asyncio.CancelledError):
                should_continue = False
                print(f"-> Keyboard interrupt received. Exiting.")
            finally:
                print("-> Killing all pulsar subscriptions and closing client.")
                if await self.cleanup(force=should_continue):
                    print("-> Pulsar connection closed.")
                else:
                    print("-> Pulsar connection already closed or client not initialized.")
                    

    async def on_join(self):
        pass

    async def loop(self):
        await asyncio.Event().wait()

    async def cleanup(self, force=False):
        if hasattr(self, 'hub'):
            await self.hub.disconnect()
        for task in self.tasks:
            task.cancel()
            if not force:
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    async def handle_exception(self, e):
        
        traceback_lines = traceback.format_tb(e.__traceback__)
        
        if traceback_lines:
            print("-----------------")
            print(traceback_lines[-1])  # Assuming you want the last line of traceback
            print(f"ERROR: {e}")
            print("-----------------")
            
        self.restart_count += 1
        if self.max_restarts is not None and self.restart_count >= self.max_restarts:
            if self.max_restarts > 0:
                print(f"-> Max restarts reached ({self.restart_count}/{self.max_restarts}). Exiting.")
            else:
                print(f"-> No restarts allowed. Exiting.")
            return False
        
        print(f"-> Restarting in {self.delay_between_restarts} seconds ({self.restart_count}/{self.max_restarts})")
        return True
    
    async def register(self, topic_name, func):
        await self.hub.register(topic_name, func)

    async def subscribe(self, topic, callback, subscription_name=None):
        await self.hub.subscribe(topic, callback, subscription_name)

    async def publish(self, topic, message=None):
        await self.hub.publish(topic, message)

    async def call(self, function_name, *args, **kwargs):
        return await self.hub.call(function_name, *args, **kwargs)

# Wraps pulsar to create a pub/sub and RPC object
class Hub:
    def __init__(self, verbose=True):
        self.client = None
        self.verbose = verbose

        self.subscription_ready_events = {}
        self.subscribe_tasks = []

        self.registered_functions = {}
        self.pending_calls = {}

    async def connect(self):
        pulsar_logger = log.getLogger("pulsar")
        pulsar_logger.setLevel(log.CRITICAL)

        self.client = await aiopulsar.connect(
            PULSAR_URL,
            logger=pulsar_logger,
        )
        
    async def disconnect(self):

        for task in self.subscribe_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        if self.client:
            await self.client.close()
            return True
        else:
            return False

    # should be _async_publish
    async def publish(self, topic, message):
        async with self.client.create_producer(topic=prefix + topic) as producer:
            await producer.send(pickle.dumps(message))
    
    # def publish(self, topic, message, blocking=False):
    #     coro = self._async_publish(topic, message)
    #     task = asyncio.create_task(coro)
        
    #     if blocking:
    #         asyncio.run(task)
            
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
                    raise

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
