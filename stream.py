import argparse
import os
import subprocess

from python_on_whales import docker


def get_git_branch():
    result = subprocess.run("git rev-parse --abbrev-ref HEAD", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        exit("Error getting git branch name")
        
    os.environ["BRANCH_NAME"] = result.stdout.strip()

def attach(service="stream"):
    print("Attaching to service: " + str(services))
    docker.execute(service, "/bin/bash")

def compose(services):
    print("Starting services: " + str(services))
    docker.compose.up(services, detach=True)

def decompose(services):
    print("Stopping services: " + str(services))
    docker.compose.down(services)

def status(services):
    containers = docker.compose.ps(services)
    longest_name = max([len(c.name) + 2 for c in containers])
    for c in containers:
        computed_ports = [c.network_settings.ports[port][0]["HostPort"] for port in c.network_settings.ports]
        adjusted_name = f"[{c.name}]".rjust(longest_name)
        print(f"{adjusted_name} created at {c.created.strftime('%m-%d %H:%M')} | Ports: {computed_ports}")

def logs(services):
    for container in docker.compose.ps(services):
        print(container.logs())
        
services = ["minecraft", "redis", "stream"]
current_branch = get_git_branch()

actions = {
    "up": {"func": compose, "default": services},
    "down": {"func": decompose, "default": services},
    "attach": {"func": attach, "default": ["stream"]},
    "status": {"func": status, "default": services},
    "logs": {"func": logs, "default": services},
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage stream docker services.")
    parser.add_argument("action", choices=actions.keys(), help="The action to perform.")
    parser.add_argument("service", nargs="?", default=None, help="Service name (default: all for start/stop, stream for attach)")
    args = parser.parse_args()
    
    # Get the function and its default services from the actions dictionary
    action_function = actions[args.action]["func"]
    default_services = actions[args.action]["default"]
    
    # If the user has provided a service, use it; otherwise, use the default
    if args.service:
        action_function([args.service])
    else:
        action_function(default_services)
        
        
        
# Future considerations:
# - Check if services are already running before starting them.
# - Incorporate BRANCH_NAME or other git-related behaviors.
# - Implement user choices/interactions.
