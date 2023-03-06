#!/bin/bash

echo "Installing requirements..."
#pip install -r requirements.txt

echo "------------------------------"

echo "Making sure the docker service is running..."
sudo service docker start

echo "------------------------------"

echo "Running crossbar docker container..."
sudo docker run -d -p 8080:8080 --name=crossbar crossbario/crossbar

echo "------------------------------"

echo "Running the minecraft server"
sudo docker run --name=minecraft -d --pull=always -e EULA=TRUE -p 25575:25575 -p 25565:25565 ghcr.io/portalhubyt/template_server_1_19:latest

echo "------------------------------"

# Save current working directory
cwd=$(pwd)

# Fill .tmux.conf file with desired settings
echo "Setting tmux options..."

cd ~
git clone https://github.com/gpakosz/.tmux.git
ln -s -f .tmux/.tmux.conf
cp .tmux/.tmux.conf.local .
sed -i '/#set -g mouse on/s|^#||' .tmux.conf.local

echo "Going back to the original directory..."
cd $cwd

echo "------------------------------"

# Create the tmux session
tmux new-session -d -s stream
tmux split-window -h
tmux split-window -h
tmux split-window -h
tmux select-pane -t 1
tmux split-window -v
tmux split-window -v
tmux select-pane -t 4
tmux split-window -v
tmux split-window -v
tmux select-pane -t 7
tmux split-window -v
tmux split-window -v
tmux select-pane -t 10
tmux split-window -v
tmux split-window -v
tmux select-layout tiled

# Run the python scripts
tmux send-keys -t 2 'python3 poster.py' C-m
tmux send-keys -t 3 'python3 parser.py' C-m
tmux send-keys -t 4 'python3 handlers/follow.py' C-m
tmux send-keys -t 5 'python3 handlers/gift.py' C-m
tmux send-keys -t 6 'python3 handlers/join.py' C-m
tmux send-keys -t 7 'python3 handlers/like.py' C-m
tmux send-keys -t 8 'python3 handlers/comment.py' C-m
tmux send-keys -t 9 'python3 handlers/share.py' C-m
tmux attach-session -t stream