import asyncio
import random
import os
import sys
import json

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from dill import dumps, loads
import shulker as mc

from tools.sanitize import pick_display, crop, sanitize
from tools.odds import pick_from_queue, flip_coin

# Work around to be able to import from the same level folder 'tools'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import config, db, pulsar, prefix

join_queue = pulsar.subscribe(prefix + "live.join", "live.join.reading")
post_queue = pulsar.create_producer(prefix + "mc.post")
lambda_queue = pulsar.create_producer(prefix + "mc.lambda")

def join_loop():
    while True:
        try:
            msg = join_queue.receive(timeout_millis=1000)
            join_queue.acknowledge(msg)
            profile = dict(loads(msg.data()))
            
            cmd = 'say ' + profile['display']
            post_queue.send(cmd.encode("utf-8"))

        except Exception as e:
            if config.verbose:
                print(e)

if __name__ == "__main__":
    print(f"Starting Join Handler...")
    join_loop()
