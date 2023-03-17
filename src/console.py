import asyncio
import datetime
import random

import shulker as mc
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion

from tools.pulsar import Portal
from tools.database import db

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Console(Portal):
    
    async def on_join(self):
        print("------------------CONSOLE------------------")
    
        self.commands = {}
        self.register_command("help", self.help, "Show this help message.")
        self.register_command("mimic", self.mimic, "Mimic n (live)-actions through pulsar", args=["action", "amount", "time_between (optional)"])
        self.register_command("sql", self.sql, "Query the database", args=["query"])
        self.register_command("post", self.sql, "Sends a minecraft commands and listen for return value", args=["cmd"])
        
        self.session = PromptSession(history=FileHistory(".console_history"),
                                     completer=CommandCompleter(self.commands),
                                     auto_suggest=ArgumentSuggest(self.commands),)
        
    async def on_exit(self):
        print("-------------------------------------------")
        exit(0)

    def register_command(self, name, func, description, args=None):
        self.commands[name] = {"func": func, "description": description, "args": args or []}

    async def help(self, *args):
        print()
        if not args or len(args) > 2:
            print(f"{bcolors.UNDERLINE}Available commands:\n")
            for command, data in self.commands.items():
                print(f"{bcolors.ENDC}o) {bcolors.BOLD}{command}{bcolors.ENDC} - {bcolors.HEADER}{data['description']}")
        elif len(args) == 1:
            command = self.commands.get(args[0])
            if command:
                print(f"{bcolors.WARNING}Usage: {args[0]} {' '.join(['<'+str(elem)+'>' for elem in command['args']])}")
            else:
                print(f"{bcolors.FAIL}Command {args[0]} not found.")
        print()
    
    async def mimic(self, action, amount, time_between=1):
        amount = int(amount)
        time_between = float(time_between)
            
        with open('tools/random_comments.txt', 'r') as f:
            random_comments = f.readlines()
            
        with open('tools/random_pseudos.txt', 'r') as f:
            random_pseudos = f.readlines()
        
        random_gift = ["Diamond", "Gold", "Silver", "Bronze"]
        random_avatars = ["https://i.imgur.com/0Z0Z0Z0.png", "https://i.imgur.com/1Z1Z1Z1.png", "https://i.imgur.com/2Z2Z2Z2.png", "https://i.imgur.com/3Z3Z3Z3.png", "https://i.imgur.com/4Z4Z4Z4.png", "https://i.imgur.com/5Z5Z5Z5.png", "https://i.imgur.com/6Z6Z6Z6.png", "https://i.imgur.com/7Z7Z7Z7.png", "https://i.imgur.com/8Z8Z8Z8.png", "https://i.imgur.com/9Z9Z9Z9.png"]
        random_role = ["Moderator", "Top Gifter", "New Gifter", "Follower", None]
        
        start = datetime.datetime.now()
        for i in range(amount):
            random_name = random.choice(random_pseudos).strip()
            profile = {
                "display": f'{i + 1}_{random_name}',
                "nickname": f'{i + 1}_{random_name}',
                "unique_id": f'{i + 1}_{random_name}',
                "user_id": random.randint(100000000, 999999999),
                "role": random.choice(random_role),
                "avatars": random_avatars,
                "followers": random.randint(0, 100000),
                "following": random.randint(0, 100000),
                "comment": random.choice(random_comments).strip(),
                "gift": random.choice(random_gift),
                "gift_value": random.randint(0, 100000),
            }
            
            await asyncio.sleep(time_between)
            time_elapsed_seconds = (datetime.datetime.now() - start).total_seconds()
            print(f"{bcolors.ENDC}({datetime.datetime.now().strftime('%H:%M')})> {bcolors.OKCYAN}{i + 1}/{amount} [{action}] in {round(time_elapsed_seconds, 2)}s", end="\r")
            await self.publish(f"live.{action}", profile)
            
        print()
    
    async def sql(self, *args):
        
        query = " ".join(args)
        if query[0] in ['"', "'"] and query[-1] in ['"', "'"]:
            query = query[1:-1]
        else:
            print(f"\n{bcolors.WARNING}The query must be typed between "" or ''.\n")

        print()
        
        ret = db.get(query)
        for unique in ret:
            
            text = ""
            
            for value in unique:
                text += str(value) + f" {bcolors.ENDC}|{bcolors.OKBLUE} "
                
            print(f"{bcolors.ENDC}-> {bcolors.OKBLUE}{text[:-7]}")
            
        print()
    
    async def post(self, *args):
        cmd = " ".join(args)
        
        if cmd[0] in ['"', "'"] and cmd[-1] in ['"', "'"]:
            cmd = cmd[1:-1]
        else:
            print(f"\n{bcolors.WARNING}The cmd must be typed between "" or ''.\n")
       
        ret = await self.call('mc.post', cmd)
        
        print(f"o> [{bcolors.GREEN}{ret}{bcolors.ENDC}]")
        
    async def loop(self):
        try:
            cmd = await self.session.prompt_async(f'({datetime.datetime.now().strftime("%H:%M")})> ')
        except KeyboardInterrupt:
            await self.on_exit()

        parts = cmd.split(" ")
        command_name = parts[0]
        args = parts[1:]
        
        if command_name in self.commands:
            command = self.commands[command_name]
            required_args = len(command["args"])
            if len(args) >= required_args and not any('' == arg for arg in args):
                await command["func"](*args)
            else:
                print(f"\n{bcolors.WARNING}Usage: {command_name} {' '.join(['<'+str(elem)+'>' for elem in command['args']])}\n")
        else:
            print(f"\n{bcolors.FAIL}Unknown command '{command_name}'. Type 'help' for a list of available commands.\n")

class CommandCompleter(Completer):
    def __init__(self, commands):
        self.commands = commands

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor

        # If there's no text or the last character is a space, don't provide any completions
        if not text.strip() or text[-1] == " ":
            return

        # Get the current word being typed
        words = text.split()
        current_word = words[-1]

        # Check if the current word matches any of the registered command names
        for name, command_data in self.commands.items():
            if name.startswith(current_word):
                yield Completion(name, start_position=-len(current_word))

class ArgumentSuggest(AutoSuggest):
    def __init__(self, commands):
        self.commands = commands

    def get_suggestion(self, buffer, document):
        text = document.text_before_cursor

        if not text.strip():
            return

        words = text.split()
        command_name = words[0]
        
        spaces = text.count(" ")
        
        if command_name in self.commands and spaces > 0 and text[-1] == " ":
            command_data = self.commands[command_name]
            
            if "args" in command_data:
                typed_args_count = spaces - 1
                
                if typed_args_count < len(command_data["args"]):
                    next_arg = command_data["args"][typed_args_count]
                    suggestion_text = f"{text.strip()} {next_arg}"
                    return Suggestion(suggestion_text[len(text):])

if __name__ == "__main__":
    console = Console()
    asyncio.run(console.run())
