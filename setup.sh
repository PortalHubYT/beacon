#!/bin/bash

# Check if script is run to reset (source setup.sh reset)
if [ ! -z "$1" ] && [ "$1" = "reset" ]; then
    # Deactivate the virtual environment
    deactivate

    # Switch back to the main branch
    git checkout main

    echo "-> Virtual environment deactivated, and switched back to the 'main' branch."

    # Update the repository to reflect the state of the main branch
    echo "-> Updating the repository to reflect the state of the 'main' branch..."
    git pull origin main
    return
fi

# Function to validate the input name
validate_name() {
    # Regex pattern to check if the name contains only letters and '-'
    pattern="^[a-zA-Z-]+$"

    if [[ $1 =~ $pattern ]]; then
        return 0  # Name is valid
    else
        return 1  # Name is invalid
    fi
}

# Function to create and activate the virtual environment
create_and_activate_venv() {
    # Check if virtual environment exists
    if [ ! -d ".pyenv" ]; then
        echo "-> Creating virtual environment '.pyenv'..."
        python3 -m venv .pyenv
    fi

    # Activate the virtual environment
    echo "-> Activating virtual environment..."
    . .pyenv/bin/activate
    
    # Installing requirements for psycopg2
    echo "-> Installing requirements for psycopg2..."
    sudo apt-get -qq install python3-dev

    # Install requirements
    echo "---------------------------"
    echo "-> Installing python requirements..."
    pip install -q -r requirements.txt
    echo "---------------------------"
}

# Check if the current branch is "main"
current_branch=$(git symbolic-ref --short HEAD)
if [[ $current_branch != "main" ]]; then
    echo "-> Error: The current branch is not 'main'. Please switch to the 'main' branch."
    return 1
fi

# Check if a name argument is provided
if [ -z "$1" ]; then
    # Read the input name from the user
    echo -n "-> Enter a name (letters and '-' only): "
    read name
else
    name="$1"
fi

# Validate the input name
if ! validate_name "$name"; then
    echo "-> Error: Invalid name. Name should contain only letters and '-'."
    return 1
fi

# Check if the branch already exists
if git rev-parse --quiet --verify "$name" > /dev/null; then
    echo "-> Branch '$name' already exists. Switching to the branch..."
    git checkout "$name"
else
    # Create and switch to a new branch with the input name
    echo "-> Creating a new branch '$name'..."
    git checkout -b "$name"
fi

# Create and/or activate the virtual environment
create_and_activate_venv

echo "-> New branch '$name' is checked out, and virtual environment '$venv_name' is created."

