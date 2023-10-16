#!/bin/bash

# Get the current branch name
current_branch=$(git rev-parse --abbrev-ref HEAD)

# Check if current branch is main
if [[ "$current_branch" == "main" ]]; then
    echo "You're currently on the main branch."

    # Prompt user for action
    PS3='What would you like to do? (Enter the number): '
    options=("Switch to another branch" "Create a new branch" "Continue on main")
    select opt in "${options[@]}"
    do
        case $opt in
            "Switch to another branch")
                echo "Available branches:"
                git for-each-ref --format="%(refname:short)" refs/ | grep -vE 'main$|HEAD$' | sed 's/^origin\///'
                read -p "Enter branch name to switch: " branch_name
                git checkout $branch_name
                current_branch=$branch_name
                break
                ;;
            "Create a new branch")
                read -p "Enter new branch name: " branch_name
                git checkout -b $branch_name
                git push -u origin $branch_name
                current_branch=$branch_name
                break
                ;;
            "Continue on main")
                break
                ;;
            *) echo "Invalid option $REPLY";;
        esac
    done
fi

# Export BRANCH_NAME for docker-compose
export BRANCH_NAME=$current_branch

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
    docker compose exec stream /bin/bash -c "export BRANCH_NAME=$current_branch && /bin/bash"
fi
