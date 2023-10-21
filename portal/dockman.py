import json
import os
import re
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Union

import requests
from python_on_whales import docker as dockpow
from python_on_whales.components.compose.models import (ComposeConfig,
                                                        ComposeConfigService)
from python_on_whales.components.container.cli_wrapper import Container

"""
NOTE: There is some non-generic logic in the Docker class to determine based
on a service_name which log manager to use.
"""

THIS_FILE_ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
LOG_FOLDER = THIS_FILE_ABSOLUTE_PATH + "/data/"

ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

class SQLiteLogger:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.conn.execute("PRAGMA journal_mode=WAL")

    def create_table(self, table_name: str):
        # Create a logs table
        self.cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            message TEXT NOT NULL
        )
        ''')
        self.conn.commit()
        
    def insert_log(self, table_name: str, logs: Union[list[str], str]):
        # If logs are a single entry, convert to a list for consistency
        if not isinstance(logs, list):
            logs = [logs]

        self.cursor.execute('BEGIN TRANSACTION')
        for message in logs:
            timestamp = self.extract_timestamp(message)
            self.cursor.execute(f'''
            INSERT INTO {table_name} (timestamp, source, log_level, message) VALUES (?, ?, ?, ?)
            ''', (timestamp, message))
        self.conn.commit()
    
    def extract_timestamp(self, log: str) -> datetime:
        log_timestamp = log.split(" ", 1)[0]
        truncated_timestamp = log_timestamp[:23] + "Z"
        return datetime.strptime(truncated_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    
    def close(self):
        self.conn.close()

@dataclass
class LogPattern:
    """Represents a pattern to match and group logs"""
    
    discriminator: str
    description: str
    sanitization: list[tuple[str, str]] = field(default_factory=list)
    # Above represents the extra sanitization to apply to the description
    # with replace, so it should be a list of tuples like: [(old, new), ...]
    
    regex: re.Pattern = field(init=False)
    frequency: int = 0
    length: int = field(init=False)
    
    def __post_init__(self):
        pattern = re.escape(self.description)
        
        for old, new in self.sanitization:
            pattern = pattern.replace(re.escape(old), re.escape(new))
            
        self.regex = re.compile(pattern)
        self.length = len(pattern)

class LogMan:
    def __init__(self, container_name: str) -> None:
        self.last_fetch: datetime = None
        self.container_name = container_name
        
    def parse_timestamp(self, log: str) -> datetime:
        last_log_timestamp = log.split(" ", 1)[0]
        truncated_timestamp = last_log_timestamp[:23] + "Z"
        return datetime.strptime(truncated_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

    def get_first_timestamp(self) -> datetime:
        logs = self.fetch(stream=True, timestamps=True)
        text = next(logs)[1].decode("utf-8")
        return self.parse_timestamp(text)
    
    def timestamp_to_int(self, timestamp: datetime) -> int:
        pass
    
    def fetch(self, **kwargs) -> list[str]:
        logs = dockpow.container.logs(self.container_name, **kwargs)
        return logs
         
class MinecraftLogger(LogMan):
    def __init__(self, container_name: str) -> None:
        self.version = "1.20.2"
        self.minecraft_locale_url = f"https://github.com/InventivetalentDev/minecraft-assets/blob{self.version}/assets/minecraft/lang/en_us.json"
        self.container_name = container_name
        self.log_generator = dockpow.container.logs(container_name, stream=True, timestamps=True)
        
        self.patterns: list[LogPattern] = []
        self.rcon_pattern = re.compile(r'\[Rcon: (.*?)\]')
        
        self.pure_log_pattern = re.compile(r'\d{4}-\d{2}-\d{2}T(\d{2}:\d{2}:\d{2}).*Z .*\[(.*?)(?::)?\](?:\:)? ([\s\S]*)')
        self.first_fetch = True
                
        self.init_rcon_patterns()
    
    def load_logs(self) -> dict:
        if not os.path.exists(LOG_FOLDER + self.container_name + ".json"):
            return None
        with open(LOG_FOLDER + self.container_name + ".json", "r") as f:
            return json.load(f)
        
    def save_logs(self, logs: list[str]) -> None:
        existing_logs = self.load_logs()
        if existing_logs is None:
            existing_logs = []
        with open(LOG_FOLDER + self.container_name + ".json", "a") as f:
            json.dump(existing_logs + logs, f, indent=4)
            
    def get_locale_file(self) -> dict[str, str]:
        locale_file = requests.get(self.minecraft_locale_url)
        return locale_file.json()
    
    def init_rcon_patterns(self) -> None:
        """Parse the Minecraft locale file to get the rcon commands
        as a LogPattern object which can be used to group logs"""

        mc_text = self.get_locale_file()
        
        identifier = "commands."
        for key, value in mc_text.items():
            if not key.startswith(identifier):
                continue
            
            self.patterns.append
            (
                LogPattern
                (
                    discriminator = key[len(identifier):],
                    description   = value,
                    sanitization  = [
                        ("%s", ".*?"),
                    ],
                )
            )

    def bootup_logs(self) -> list[str]:
        logs = []
        for source, log in self.log_generator:
            log = log.decode("utf-8")
            log = re.sub(ANSI_ESCAPE, "", log)
            if "[Rcon: " in log:
                break
            
            match = re.search(self.pure_log_pattern, log)
            if match:
                time, level, message = match.groups()
                if "Server thread" in level:
                    level = level.split("/")[1]
                log = f"{time} | [{level}] {message}"
            else:
                log = f"{' ' * 9}| {message}"
            logs.append(log)
        self.save_logs(logs)
        return logs
    
    def fetch(self):
        if self.first_fetch:
            self.first_fetch = False
            return self.bootup_logs()
            
    def group_logs(self, logs: list[str]) -> dict[str, list[str]]:
        
        self.pull_count += 1
        if self.pull_count >= 10:
            self.check_first = sorted()
            self.pull_count = 0
            pattern_freq.clear()
            
        grouped_logs = {}
        normal_logs = []
        pattern_list = check_first + sorted_patterns
        
        for line in logs:
            if "[Rcon: " not in line:
                normal_logs.append(line)
                continue
            
            clean_line = ANSI_ESCAPE.sub('', line)

            for key in pattern_list:
                if regex_patterns[key].search(clean_line):
                    grouped_logs[key] = grouped_logs.get(key, []) + [line]
                    pattern_freq[key] = 1 if key not in pattern_freq else pattern_freq[key] + 1
                    break

        return normal_logs, grouped_logs
         
        
@dataclass
class Docker:
    service: str
    container: str
    port: list[dict]
    config: ComposeConfigService
    logs_manager: LogMan = field(init=False)
    
    def __post_init__(self):
        if self.service == "minecraft_server":
            self.logs_manager = MinecraftLogger(self.container)
        else:
            self.logs_manager = LogMan(self.container)

    @property
    def logs(self) -> list[str]:
        return self.logs_manager.fetch()
    
class Compose:
    def __init__(self):
        self.logger: SQLiteLogger = SQLiteLogger("logs.db")
        self.config: ComposeConfig  = dockpow.compose.config()
        self.services: list[tuple[str, ComposeConfigService]] = self.config.services.items()
        self.dockers: list[Docker] = self.get_dockers()
        
    @staticmethod
    def get_exposed_ports(service_data: ComposeConfigService) -> list[dict[int, int]]:
        ports = []
        if not service_data.ports:
            return ports
        
        for port in service_data.ports:
            ports.append({"published": port.published, "target": port.target})
        return ports
        
    def get_dockers(self) -> list[Docker]:
        members = []
        for service, data in self.services:
            self.logger.create_table(service)
            member = Docker(
                service     = service,
                container   = data.container_name,
                port        = self.get_exposed_ports(data),
                config      = data,
            )
            members.append(member)
        return members

    def get_docker(self, name: str) -> Union[Docker, None]:
        for docker in self.dockers:
            if docker.container == name:
                return docker
            elif docker.service == name:
                return docker
        return None
    
    def get_dockers_status(self) -> dict[str, bool]:
        container_status = {}
        running = [container.name for container in dockpow.container.list()]
        for docker in self.dockers:
            container_status[docker.container] = docker.container in running
        return container_status
