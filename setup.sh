#!/bin/bash

#######################################################################
############################# ARG = reset #############################

# Check if script is run to reset (source setup.sh reset)
if [ ! -z "$1" ] && [ "$1" = "reset" ]; then
    # Deactivate the virtual environment
    deactivate

    # Switch back to the main branch
    git checkout main

    echo "\n-> Virtual environment deactivated, and switched back to the 'main' branch."

    # Update the repository to reflect the state of the main branch
    echo "\n-> Updating the repository to reflect the state of the 'main' branch..."
    git pull origin main
    return 0
fi

#######################################################################
############################## FUNCTIONS ##############################

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
        echo "\n-> Creating virtual environment '.pyenv'..."
        python3 -m venv .pyenv
    fi

    # Activate the virtual environment
    echo "\n-> Activating virtual environment..."
    . .pyenv/bin/activate
    
    
    echo "\n-> Running apt-get update..."
    sudo apt-get -qq update

    # Installing requirements for psycopg2
    echo "\n-> Installing requirements for psycopg2..."
    sudo apt-get -qq install python3-dev

    # Install requirements
    echo "\n---------------------------"
    echo "-> Installing python requirements...\n"
    pip install -q -r requirements.txt
    echo "\n---------------------------"
}

#######################################################################
################################ MAIN #################################

# 1. Check if the current branch is "main"
current_branch=$(git symbolic-ref --short HEAD)
if [[ $current_branch != "main" ]]; then
    echo "\n-> Error: The current branch is not 'main'. Please switch to the 'main' branch."
    return 1
fi

################################

# 2. Check if a name argument is provided
if [ -z "$1" ]; then
    # Read the input name from the user
    echo -n "\n-> Enter a name (letters and '-' only): "
    read name
else
    name="$1"
fi

################################

# 3. Validate the input name
if ! validate_name "$name"; then
    echo "\n-> Error: Invalid name. Name should contain only letters and '-'."
    return 1
fi

################################

# 4. Check if the branch already exists
if git rev-parse --quiet --verify "$name" > /dev/null; then
    echo "\n-> Branch '$name' already exists. Switching to the branch..."
    git checkout "$name"
else
    # Create and switch to a new branch with the input name
    echo "\n-> Creating a new branch '$name'..."
    git checkout -b "$name"
fi

echo "\n-> Switched to branch '$name'"

################################

# 5. Create and/or activate the virtual environment
create_and_activate_venv

################################

# 6. Modify the README.md file (if it is the default template)
echo "\n-> Modifying the README.md file..."

filename="README.md"
first_line=$(head -n 1 "$filename")

# Check if the first line is "Default Template"
if [[ "$first_line" == "# Default Template" ]]; then

    # Replace hyphen with space and capitalize first letters
    pretty_name=$(echo "$name" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')
    
    # Replace the first line with "#" + the variable $name  
    sed -i "1s/.*/# $pretty_name/" "$filename"

    # Prompt the user for a brief description
    echo -n "Enter a one-line description of what the stream is about: "
    read description

    # Replace the lines between the start and end lines with the user's description
    sed -i "3s/.*/$description/" "$filename"

     # Git commands
    git add README.md
    git commit -m "Modified README.md"
    git push --set-upstream origin "$name"

    echo "\n-> README.md modified and pushed successfully."
else
    echo "\n-> First line of the README is not 'Default Template'. No modifications made."
fi

################################

# 7. Start the docker deamon
echo "\n-> Starting the docker deamon...\n"
sudo service docker start

################################

# 8. Prompt user to stop and kill all running docker containers
echo "-----------------------------------------------------------"
sudo docker container ps
echo "-----------------------------------------------------------"
echo -n "\n-> Do you wish to stop and kill all running docker containers? (y/n): "
read answer

if [[ $answer == "y" || $answer == "Y" ]]; then
    echo "\n-> Stopping and killing all running docker containers..."

    # Stop running containers
    running_containers=$(sudo docker container ls -q)
    if [[ -n $running_containers ]]; then
        sudo docker container stop $running_containers
        echo "\n-> Stopped the following containers:"
        echo $running_containers
    else
        echo "\n-> No running containers to stop."
    fi

    # Remove containers
    all_containers=$(sudo docker container ls -aq)
    if [[ -n $all_containers ]]; then
        sudo docker container rm $all_containers
        echo "\n-> Removed the following containers:"
        echo $all_containers
    else
        echo "\n-> No containers to remove."
    fi

    echo "\n-> All running docker containers have been stopped and killed."

    # Prompt user if they want to prune docker
    echo "\n-> Do you wish to delete all unused docker images, containers, networks and volumes?\n"
    sudo docker system prune --volumes

else
    echo "\n-> No docker containers were stopped or killed."
fi

################################






