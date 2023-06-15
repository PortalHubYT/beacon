import asyncio
import datetime
import os

import shulker as mc
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion

from tools.pulsar import Portal
from tools.database import db
from tools.mimic import gen_fake_profiles

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

# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)

# Get the directory containing the current file
directory = os.path.dirname(current_file_path)

# Construct the absolute file path by joining the directory and the desired file name
log_file_path = os.path.join(directory, 'tools/logs/console_history.log')

class Console(Portal):
    
    async def on_join(self):
        print("------------------CONSOLE------------------")
    
        self.commands = {}
        self.register_command("help", self.help, "Show this help message.")
        self.register_command("mimic", self.mimic, "Mimic n (live)-actions through pulsar", args=["action", "amount", "time_between (optional)"])
        self.register_command("sql", self.sql, "Query the database", args=["query"])
        self.register_command("post", self.post, "Sends a minecraft commands and listen for return value", args=["cmd"])
        self.register_command("reset_db", self.reset_db, "Reset the database specified in tools/.env, requires 'confirm' as arg", args=["confirm"])

        self.session = PromptSession(history=FileHistory(log_file_path),
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
        
        profiles = gen_fake_profiles(amount)
        
        start = datetime.datetime.now()
        for i, profile in enumerate(profiles):
            
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
            print(f"\n{bcolors.WARNING}The cmd must be typed between \"\" or ''.{bcolors.ENDC}\n")
            return
       
        ret = await self.call('mc.post', cmd)
        
        print(f"o> [{bcolors.OKGREEN}{ret}{bcolors.ENDC}]")

    async def reset_db(self, *args):
        if len(args) == 0:
            print("You need to confirm the reset of the database by typing 'reset_db confirm'.")
        elif len(args) == 1 and args[0] == "confirm":
            print("\n-> Resetting database...")
            db.reset_database(confirm=True)
            print("Database reset.\n")
       
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
