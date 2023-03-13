#!/bin/bash

if [[ "$@" == *"--install"* ]]; then
    echo "Installing requirements..."
    sudo apt-get update
    sudo apt-get install libpq-dev
    pip install -r requirements.txt --upgrade

fi

if [[ "$@" == *"--prune"* ]]; then
    echo "Pruning docker images..."
    sudo docker system prune -a
fi

if [[ "$@" == *"--crossbar"* || "$@" == *"--docker"* ]]; then
  if [[ "$@" == *"--restart"* ]]; then
    echo "Restarting docker containers..."
    sudo docker compose down
  fi
  sudo docker compose up crossbar -d 
fi

if [[ "$@" == *"--postgres"* || "$@" == *"--docker"* ]]; then
  if [[ "$@" == *"--restart"* ]]; then
    echo "Restarting docker containers..."
    sudo docker compose down
  fi
  sudo docker compose up postgres -d 
fi

if [[ "$@" == *"--minecraft"* || "$@" == *"--docker"* ]]; then
  if [[ "$@" == *"--restart"* ]]; then
    echo "Restarting docker containers..."
    sudo docker compose down
  fi
  sudo docker compose up minecraft -d 
fi

# Save current working directory
cwd=$(pwd)

cd ~

if [ ! -d ".tmux" ]; then
  # Fill .tmux.conf file with desired settings
  echo "Preparing tmux options..."
  git clone https://github.com/gpakosz/.tmux.git
  ln -s -f .tmux/.tmux.conf
  cp .tmux/.tmux.conf.local .
  sed -i '/#set -g mouse on/s|^#||' .tmux.conf.local
fi

cd $cwd

if tmux has-session -t stream >/dev/null 2>&1; then
    echo "Attaching to existing session..."
    tmux attach-session -t stream
    exit
fi

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
# parse the args to see if there's "-run"
if [[ "$@" == *"--run"* ]]; then
    echo "Running the scripts..."
    tmux send-keys -t 1 'python3 components/collector.py' C-m
    tmux send-keys -t 2 'python3 components/poster.py' C-m
    tmux send-keys -t 3 'python3 components/handler.py' C-m
    tmux send-keys -t 4 'python3 components/follow.py' C-m
    tmux send-keys -t 5 'python3 components/gift.py' C-m
    tmux send-keys -t 6 'python3 components/join.py' C-m
    tmux send-keys -t 7 'python3 components/like.py' C-m
    tmux send-keys -t 8 'python3 components/comment.py' C-m
    tmux send-keys -t 9 'python3 components/share.py' C-m
fi

if [[ "$@" == *"--headless"* ]]; then
    exit
fi

tmux attach-session -t stream

echo "Done!"