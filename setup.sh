#!/bin/bash

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
        echo "Creating virtual environment '.pyenv'..."
        python3 -m venv .pyenv
    fi

    # Activate the virtual environment
    echo "Activating virtual environment..."
    source .pyenv/bin/activate

    # Install requirements
    echo "Installing requirements..."
    pip install -r requirements.txt
}

# Check if the current branch is "main"
current_branch=$(git symbolic-ref --short HEAD)
if [[ $current_branch != "main" ]]; then
    echo "Error: The current branch is not 'main'. Please switch to the 'main' branch."
    exit 1
fi

# Read the input name from the user
echo -n "Enter a name (letters and '-' only): "
read name

# Validate the input name
if ! validate_name "$name"; then
    echo "Error: Invalid name. Name should contain only letters and '-'."
    exit 1
fi

# Check if the branch already exists
if git rev-parse --quiet --verify "$name" > /dev/null; then
    echo "Branch '$name' already exists. Switching to the branch..."
    git checkout "$name"
else
    # Create and switch to a new branch with the input name
    echo "Creating a new branch '$name'..."
    git checkout -b "$name"
fi

# Create and/or activate the virtual environment
create_and_activate_venv

echo "New branch '$name' is checked out, and virtual environment '$venv_name' is created."

