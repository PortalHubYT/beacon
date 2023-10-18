import datetime
import os
import re
from typing import Union

import termcolor
from python_on_whales import docker
from retriever import STREAM_GENERAL_INFO, STREAM_GENERAL_LOGS
from rich.console import ConsoleRenderable
from rich.text import Text
from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import (Container, Grid, Horizontal, HorizontalScroll,
                                Vertical, VerticalScroll)
from textual.screen import Screen
from textual.widgets import (Button, Collapsible, ContentSwitcher, Input,
                             Label, Log, Markdown, MarkdownViewer, Placeholder,
                             RichLog, Static, TabbedContent, TabPane, Tabs,
                             TextArea)

# Container name of the service
DOCKER_SERVICES = {
    "server": "minecraft_server",
    "redis": "redis_deamon",
    "stream": "tiktok_stream"
}

# ["server", "redis", "stream"]
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

### CUSTOM WIDGETS  ###

class DockerLog(RichLog):
    def __init__(self, container_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.container_name = container_name
        self._last_log_size = 0

    async def on_mount(self, event: events.Mount) -> None:
        self.set_interval(1, self.fetch_docker_logs)
        self.set_timer(2, lambda: self.write("Resuming from most recent logs above...!"))

    def fetch_docker_logs(self) -> None:
        """Fetch new logs from the Docker container and update the Log widget."""
        logs = docker.container.logs(self.container_name, tail=1000)
        
        # Split the logs into individual lines
        lines = logs.splitlines()

        # Determine new lines since the last update
        new_lines = lines[self._last_log_size:]
        
        if not new_lines:
            return
        else:
            new_lines = [ANSI_ESCAPE.sub('', line) for line in new_lines]
        
        # Update the Log widget with new content
        self.write("\n".join(new_lines))

        # Update our current position in the logs
        self._last_log_size = len(lines)

class FileLog(RichLog):
    def __init__(self, filename: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename
        self._file_descriptor = None
        self._file_position = 0

    async def on_mount(self, event: events.Mount) -> None:
        self._file_descriptor = open(self.filename, 'rb')
        self.set_interval(1, self.read_from_file)

    def read_from_file(self) -> None:
        """Read new lines from the file and update the Log widget."""
        file_size = os.stat(self.filename).st_size
        bytes_to_read = min(file_size, 1000 * 200)  # assuming average line length is 200 bytes
        
        # Handle edge case where file is less than the bytes_to_read
        if file_size > bytes_to_read:
            self._file_descriptor.seek(-bytes_to_read, os.SEEK_END)

        content = self._file_descriptor.read().decode('utf-8')  # decode the bytes to string
        
        # Split into lines and keep only the last 1000
        new_lines = content.splitlines()[-1000:]
        
        if not new_lines:
            return
        else:
            new_lines = [ANSI_ESCAPE.sub('', line) for line in new_lines]
        
        # Update the Log widget with new content
        self.write("\n".join(new_lines))

        # Update our current position in the file
        self._file_position = self._file_descriptor.tell()

    async def on_unmount(self, event: events.Unmount) -> None:
        # Close the file descriptor when we're done with it
        if self._file_descriptor:
            self._file_descriptor.close()


###     VIEWS       ###

class Dashboard(Grid):

    def compose(self) -> ComposeResult:
        console = Input("t", classes="command_input")
        console.border_title = "Console"
        yield console
        
        stream_info = Markdown(STREAM_GENERAL_INFO, classes="info_box")
        stream_info.border_title = "Stream Info"
        yield stream_info
        
        stream_log = FileLog(STREAM_GENERAL_LOGS, classes="file_log", auto_scroll=True, max_lines=1000, wrap=True, highlight=True)
        stream_log.border_title = "Stream Log"
        yield stream_log
        
class MinecraftServer(Vertical):
    def compose(self) -> ComposeResult:
        console = Input("t", classes="command_input", id="minecraft_server_console")
        console.border_title = "Console"
        yield console
        
        server_log = DockerLog(DOCKER_SERVICES["server"], classes="file_log", id="minecraft_server_logs", auto_scroll=True, max_lines=1000, wrap=True, highlight=True)
        server_log.border_title = "Server Log"
        yield server_log
   

###     MAIN       ###

class Navbar(Static):
    BINDINGS: list[BindingType] = [
    Binding("left", "previous_tab", "Previous tab", show=False),
    Binding("right", "next_tab", "Next tab", show=False),
    Binding("down", "select_content", "Select content", show=False),]
        
    def compose(self) -> ComposeResult:
        with TabbedContent(id="navbar_tabs"):
            with TabPane("Dashboard"):
                yield Dashboard(id="dashboard")
            with TabPane("Minecraft Server"):
                yield MinecraftServer(id="minecraft_server")
            with TabPane("Docker"):
                yield Placeholder()
                
    def action_select_content(self) -> None:
        """Select the content switcher."""
        tabs = self.get_child_by_type(TabbedContent)

        dashboard = tabs.get_widget_by_id("dashboard")
        dashboard_console = dashboard.get_child_by_type(Input)
        
        tab_id = tabs.active
        tabs.blur()
        if tab_id == "tab-1":
            dashboard_console.focus()

class Footer(Static):
    
    date = lambda self: datetime.datetime.now().strftime("%d/%m")
    hour = lambda self: datetime.datetime.now().strftime("%H:%M:%S")
    separator = lambda self: " | "
    
    def compose(self) -> ComposeResult:
        with Horizontal(id="footer_data"):
            yield Label(self.date(), id="footer_date")
            yield Label(self.separator(), classes="footer_separator")
            yield Label(self.hour(), id="footer_clock")
            yield Label(self.separator(), classes="footer_separator")
            yield RichLog(id="footer_docker_status")

    async def on_mount(self, event: events.Mount) -> None:
        self.set_interval(1, self.update_status)
        self.set_docker_status()

    @staticmethod
    def get_docker_status() -> dict:
        """Using the DOCKER_SERVICES variable, check if the services are running.
        Returns a dict of pretty_name: boolean"""
        status = {}
        for pretty_name, service in DOCKER_SERVICES.items():
            try:
                container = docker.container.inspect(service)
                status[pretty_name] = container.state.running
            except:
                status[pretty_name] = False
        return status
        
    def set_docker_status(self) -> str:
        status_bar: RichLog = self.children[0].get_child_by_id("footer_docker_status")
        pretty = {
            False: Text("NO", style="bold red"),
            True: Text("OK", style="bold green")
        }
        state = self.get_docker_status()
        
        pre_compute: list[Text] = []
        for container in state:
            # Service name
            pre_compute.append(Text(container.capitalize()))
            # Separator
            pre_compute.append(Text(": "))
            # Service status
            pre_compute.append(pretty[state[container]])
            # Services separator
            pre_compute.append(Text("  "))

        computed = Text.assemble(*pre_compute)
        status_bar.write(computed)
        return ""
        # w = self.app.get_widget_by_id("Footer")
        # print(dir(w))
        # footer = self.get_widget_by_id("footer_data")
        # id_base = "footer_docker_status_"
        # for pretty_name, service in DOCKER_SERVICES.items():
        #     curr_id = id_base + pretty_name
        #     # First we check if a widget with the service name exists
        #     try:
        #         widget = self.get_widget_by_id(curr_id)
        #     except:
        #         footer.get_widget_by_id("footer_data").append(Label("", id=curr_id))

        # return
        # docker_status = ConsoleRenderable()
        # ok = "OK"
        # no = "NO"
        

        # docker_status = ""
        # for pretty_name, service in DOCKER_SERVICES.items():
        #     status = f"{pretty_name.capitalize()}: {no}   "
        #     try:
        #         container = docker.container.inspect(service)
        #         if container.state.running:
        #             status = f"{pretty_name.capitalize()}: {ok}   "
        #     except:
        #         pass
        #     docker_status += status
            
        # return docker_status
    

    def update_status(self) -> None:
        """Update the hour."""

        clock: Static = self.get_widget_by_id("footer_clock")
        clock.update(self.hour())
        
        date: Static = self.get_widget_by_id("footer_date")
        date.update(self.date())
        
        self.set_docker_status()
        
        
          
class Portal(Screen):
    
    BINDINGS: list[BindingType] = [
    Binding("escape", "return_to_navbar", "Return to navbar", show=False),]
        
    def compose(self) -> ComposeResult:
        
        yield Navbar(id="Navbar")
        yield Footer(id="Footer")
        
    def action_return_to_navbar(self) -> None:
        """Return to the navbar."""
        navbar = self.query_one(Tabs)
        self.set_focus(navbar)
        
class LayoutApp(App):
    CSS_PATH = "portal.tcss"
    def on_mount(self) -> None:
        self.push_screen(Portal())


if __name__ == "__main__":
    app = LayoutApp()
    app.run()
