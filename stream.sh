#!/bin/bash

# Define an array of services
declare -a services=("minecraft" "redis" "stream")

# Variable to check if all services are up
all_up=true

# Loop through each service to check its status
for service in "${services[@]}"
do
    # Use docker compose to check if the service is up
    if ! docker compose ps ${service} | grep -q Up; then
        echo "${service} is not running. Starting it..."
        docker compose up -d ${service}
        all_up=false
    fi
done

# If all services are up, attach to stream
if ${all_up}; then
    echo "All services are running. Attaching to stream..."
    docker compose exec stream /bin/bash
fi
