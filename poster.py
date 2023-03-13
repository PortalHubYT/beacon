import asyncio
import sys
import os

from dill import loads
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from dotenv import load_dotenv

from config import config, db, pulsar, prefix
import shulker as mc

MINECRAFT_IP = os.getenv("MINECRAFT_IP")
MINECRAFT_RCON_PASSWORD = os.getenv("MINECRAFT_RCON_PASSWORD")
MINECRAFT_RCON_PORT = os.getenv("MINECRAFT_RCON_PORT")

fail = f"Failed to connect to: {MINECRAFT_IP}:{MINECRAFT_RCON_PORT} (password: {MINECRAFT_RCON_PASSWORD})"
success = f"Connected to: {MINECRAFT_IP}:{MINECRAFT_RCON_PORT} (password: {MINECRAFT_RCON_PASSWORD})"

regular_post_queue = pulsar.subscribe(prefix + "mc.post", "mc.post.reading")
lambda_post_queue = pulsar.subscribe(prefix + "mc.lambda", "mc.lambda.reading")

def post_loop():
  while True:
    try:
        msg = regular_post_queue.receive(timeout_millis=10)
        regular_post_queue.acknowledge(msg)
        cmd = msg.data().decode("utf-8")
        ret = mc.post(cmd)
        
        if config.verbose:
            print(f"===============")
            print(f"[CMD]->[{cmd}]")
            print(f"[RET]->[{ret}]")
            print(f"===============")
            
    except Exception as e:
        if config.verbose:
            print(e)
    
    try:
        msg = lambda_post_queue.receive(timeout_millis=10)
        lambda_post_queue.acknowledge(msg)
        data = msg.data().decode("utf-8")
        instruction = loads(data)
        ret = instruction()
        
    except Exception as e:
        if config.verbose:
            print(e)
    

if __name__ == "__main__":
    print(f"Starting Poster...")
    print("Trying to connect to minecraft server...")
    try:
        mc.connect(MINECRAFT_IP, MINECRAFT_RCON_PASSWORD, port=MINECRAFT_RCON_PORT)
        print(success)
    except Exception as e:
        print(fail)
        print(f"Error: {e}")
        exit(1)
  
    post_loop()
