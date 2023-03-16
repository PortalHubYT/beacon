import asyncio
import aiopulsar
import pulsar

from pulsar import AuthenticationToken

from config import PULSAR_URL, prefix, PULSAR_TOKEN, pulsar_logger

async def test_publish(client, topic, message):
    await asyncio.sleep(5)  # Add a delay before publishing the message
    async with client.create_producer(topic=prefix + topic) as producer:
        await producer.send(message.encode('utf-8'))
        print(f"Published message: {message}")

async def test_subscribe(client, topic):
    async with client.subscribe(
        topic=prefix + topic,
        subscription_name='my-subscription',
        consumer_name="my-consumer-dad",
        initial_position=pulsar.InitialPosition.Earliest,
    ) as consumer:
        while True:
            msg = await consumer.receive()
            print(f"Received message: {msg.data().decode('utf-8')}")
            await consumer.acknowledge(msg)

async def test_example():
    topic = "test-topico"

    async with aiopulsar.connect(PULSAR_URL, authentication=AuthenticationToken(PULSAR_TOKEN), logger=pulsar_logger) as client:
        subscribe_task = asyncio.create_task(test_subscribe(client, topic))
        publish_task = asyncio.create_task(test_publish(client, topic, "Hello, Pulsar!"))

        await asyncio.gather(subscribe_task, publish_task)

loop = asyncio.get_event_loop()
loop.run_until_complete(test_example())
