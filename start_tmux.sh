# Create a new tmux session named "stream"
tmux new-session -d -s stream

# Split the window into multiple panes
tmux split-window -v
tmux split-window -v
tmux select-pane -t 1
tmux split-window -h
tmux select-pane -t 3
tmux split-window -h
tmux split-window -h

# Get the width of the screen
screen_width=$(tmux display-message -p '#{window_width}')

# Calculate the desired width for the pane
pane_width=$((screen_width * 33 / 100))

# Resize the panes
tmux select-pane -t 3
tmux resize-pane -x "$pane_width"
tmux resize-pane -y 25
tmux select-pane -t 4
tmux resize-pane -x "$pane_width"
tmux select-pane -t 5
tmux resize-pane -x "$pane_width"

# Go to each pane and activate the "venv_skrib" Python virtual environment
tmux select-pane -t 0
tmux send-keys "source ./venv_skrib/bin/activate" C-m
tmux select-pane -t 1
tmux send-keys "source ./venv_skrib/bin/activate" C-m
tmux select-pane -t 2
tmux send-keys "source ./venv_skrib/bin/activate" C-m
tmux select-pane -t 3
tmux send-keys "source ./venv_skrib/bin/activate" C-m
tmux select-pane -t 4
tmux send-keys "source ./venv_skrib/bin/activate" C-m
tmux select-pane -t 5
tmux send-keys "source ./venv_skrib/bin/activate" C-m

# Attach to the tmux session
tmux attach-session -t stream
