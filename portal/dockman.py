import re
from dataclasses import dataclass
from typing import Union

from python_on_whales import docker as dockpow
from python_on_whales.components.compose.models import (ComposeConfig,
                                                        ComposeConfigService)
from python_on_whales.components.container.cli_wrapper import Container

ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

@dataclass
class Docker:
    service: str
    container: str
    port: list[dict]
    running: bool
    logs: list[str]
    config: ComposeConfigService
    
class Compose:
    def __init__(self):
        self.config: ComposeConfig = dockpow.compose.config()
        self.services: list[tuple[str, ComposeConfigService]] = self.config.services.items()
        self.containers: list[Container] = dockpow.compose.ps()
        self.running: list[str] = [container.name for container in self.containers]
        self.dockers: list[Docker] = self.get_dockers()
    
    @staticmethod
    def get_logs(container_name: str) -> list[str]:
        logs = dockpow.container.logs(container_name, tail=1000)
        return logs.splitlines()
    
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
            member = Docker(
                service     = service,
                container   = data.container_name,
                port        = self.get_exposed_ports(data),
                running     = data.container_name in self.running,
                logs        = self.get_logs(data.container_name),
                config      = data,
            )
            members.append(member)
        return members


comp = Compose()
for docker in comp.dockers:
    print(docker.container, docker.service)

exit()
class Nonee:
    def is_running(self, service_name: str) -> bool:
        return container_name in self.running
    
    @property
    def services(self) -> list[str]:
        return list(docker.compose.config().services.keys())
    
    @staticmethod
    def match(name: str) -> Union[tuple[str, str], None]:
        """Return the service name of a fleet member by trying to match
        either by service name or container name."""
        
        config = docker.compose.config()
        for service, data in config.services.items():
            if name in [service, data.container_name]:
                return {"service": service, "container": data.container_name}
        return None
    
    @property
    def member_data(self) -> list[dict]:
        """Return a list of dictionnaries containing the data of each member
        of the compose."""
        config = docker.compose.config()
        return [
            {
                "service": key,
                "container": value.container_name,
                "port":
                [
                    {
                        "published": port.published,
                        "target": port.target
                    }
                    for port in value.ports
                ]
                if value.ports
                else None,
            }
            for key, value in config.services.items()
        ]
    @staticmethod
    def get_compose_data() -> dict:
        config = docker.compose.config()
        fleet = ...
        return [
            {
                "service": key,
                "container": value.container_name,
                "port":
                [
                    {
                        "published": port.published,
                        "target": port.target
                    }
                    for port in value.ports
                ]
                if value.ports
                else None,
            }
            for key, value in config.services.items()
        ]
        
    def exists(self, name: str) -> bool:
        """Check if the docker exists in the compose file.
        Return the docker data if it exists, else None."""
        compose_data = self.get_compose_data()
        exists = None
        for docker in compose_data:
            if name in [docker["service"], docker["container"]]:
                exists = docker
                break
        return exists
        
    def get_info(self, name: str, full_config: bool = False) -> dict:
        """Get the docker data from the compose file."""
        fleet_member = self.exists(name)
        
        if not fleet_member:
            raise ValueError(f"Docker '{name}' not found in the compose file.")
        
        fleet_member["running"] = False
        if fleet_member["container"] in self.running:
            fleet_member["running"] = True
        
        logs = docker.container.logs(fleet_member["container"], tail=1000)
        fleet_member["logs"] = logs.splitlines()
        
        if full_config:
            fleet_member["config"] = docker.compose.config().services[fleet_member["service"]]

        return fleet_member

compose_manager = ComposeManager()
res = compose_manager.match("server")
print(res)
### CUSTOM WIDGETS  ###
exit()
class DockerLog(RichLog):
    def __init__(self, container_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.container_name = container_name
        self._last_log_size = 0

    async def on_mount(self, event: events.Mount) -> None:
        self.set_interval(1, self.fetch_docker_logs)
        self.set_timer(
            2, lambda: self.write("Resuming from most recent logs above...!")
        )

    def fetch_docker_logs(self) -> None:
        """Fetch new logs from the Docker container and update the Log widget."""
        logs = docker.container.logs(self.container_name, tail=1000)

        # Split the logs into individual lines
        lines = logs.splitlines()

        # Determine new lines since the last update
        new_lines = lines[self._last_log_size :]

        if not new_lines:
            return
        else:
            new_lines = [ANSI_ESCAPE.sub("", line) for line in new_lines]

        # Update the Log widget with new content
        self.write("\n".join(new_lines))

        # Update our current position in the logs
        self._last_log_size = len(lines)
