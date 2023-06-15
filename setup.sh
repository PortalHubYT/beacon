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

# Create a new virtual environment
venv_name="tiktok_stream_$name"
echo "Creating a new virtual environment '$venv_name'..."
python3 -m venv "$venv_name"

# Check if the name is already in .gitignore
if ! grep -q "$venv_name/" .gitignore; then
    # Append the virtual environment name to .gitignore
    echo "$venv_name/" >> .gitignore
    echo "Added '$venv_name/' to .gitignore."
else
    echo "'$venv_name/' is already in .gitignore. Skipping."
fi

# Activate the new virtual environment
source "$venv_name/bin/activate"

echo "New branch '$name' is checked out, and virtual environment '$venv_name' is created."

