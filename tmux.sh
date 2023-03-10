#!/bin/bash
if [[ $1 == "--install" ]]; then
    echo "Installing requirements..."
    sudo apt-get install libpq-dev
    pip install -r requirements.txt --upgrade

fi

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
# parse the args to see if there's "-run"
if [[ $1 == "--run" ]]; then
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