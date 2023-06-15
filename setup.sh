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
    echo "\n-> Branch '$name' already exists. Switching to the branch...\n"
    git checkout "$name"
else
    # Create and switch to a new branch with the input name
    echo "\n-> Creating a new branch '$name'..."
    git checkout -b "$name"
fi

# Check the exit status of the previous git checkout command
if [ $? -ne 0 ]; then
    echo "\n-> Failed to switch to branch '$name'. Exiting the script.\n"
    exit 1
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

# 9. Running the minecraft docker container and prompting for new world

echo -n "\n-> Do you wish to create a new world? (y/n): "
read answer

if [[ $answer == "y" || $answer == "Y" ]]; then
    sudo rm -rf volumes/world/*
else
    echo "\n-> Using the existing world..."
fi

echo "\n-> Running the minecraft server docker container...\n"
sudo docker compose up minecraft -d

echo "\n-> Waiting for the Minecraft server to start...\n"

# Loop until the desired message is found
while true; do
  # Read the last line of the container's logs
  container_logs=$(sudo docker logs minecraft)

  # Check if the desired message is found
  if [[ $container_logs == *"Done ("* ]]; then
    echo "\n-> Minecraft server is running!"
    break  # Exit the loop
  fi

  sleep 1  # Wait for 1 second before checking again
done

################################

# 10. Prompt the user to fill in the .env file with the relevant keys

dotenv_file="src/tools/.env"

# Function to prompt for a value
prompt_value() {
    echo -n "\n-> Enter the value for $1: "
    read value

    echo "$1=$value" >> "$dotenv_file"
    echo
    echo "---> Set $1 = $value\n"
}

# Check if dotenv file already exists
if [[ -e "$dotenv_file" ]]; then
    echo "-> The dotenv file already exists: $dotenv_file"

    echo -n "\n-> Do you want to overwrite it? (y/n): "
    read overwrite

    if [[ "$overwrite" = "y" ]]; then
        # Create or overwrite the dotenv file
        echo "\n-> Creating dotenv file: $dotenv_file\n"

        # Prompt for each value
        prompt_value "POSTGRES_USER"
        prompt_value "POSTGRES_PASSWORD"
        prompt_value "POSTGRES_DB"
        prompt_value "POSTGRES_HOST"
        prompt_value "POSTGRES_PORT"
        prompt_value "MINECRAFT_IP"
        prompt_value "MINECRAFT_RCON_PORT"
        prompt_value "MINECRAFT_RCON_PASSWORD"
        prompt_value "PULSAR_URL"
        prompt_value "PULSAR_TOKEN"
        prompt_value "PULSAR_NAMESPACE"

        echo "\n-> Dotenv file created successfully!\n"
    fi
fi

################################

# 11. Check if the database login details are correct and if it's empty or needs to be

python3 status.py check_database

if [ $? -eq 1 ]; then
    return 1
fi

#####

python3 status.py check_tables_empty

if [ $? -eq 1 ]; then
    echo -n "\n-> Would you like to reset the database? (y/n): "
    read answer

    if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
        python3 status.py reset_database
    fi

fi

################################

# 12. Check if the pulsar login details are correct and if the connection is successful

python3 status.py check_pulsar

if [ $? -eq 1 ]; then
    return 1
fi