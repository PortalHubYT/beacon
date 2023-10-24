#!/bin/bash

# Ensure a numeric argument is provided
if ! [[ "$1" =~ ^[0-9]+$ ]]; then
    echo "Please provide a numeric argument."
    exit 1
fi

# Create a new tmux session named "stream"
tmux new-session -d -s stream

# Determine the dimensions of the grid
panes=$1
sqrt=$(echo "sqrt($1)" | bc)
closest_square=$(( sqrt * sqrt ))

if [[ $closest_square -eq $panes ]]; then
    rows=$sqrt
    cols=$sqrt
else
    rows=$(( sqrt + 1 ))
    cols=$sqrt
    remainder=$(( panes - closest_square ))
fi

# Create the grid of panes
created_panes=1
for (( r=0; r<rows; r++ )); do
    for (( c=0; c<cols; c++ )); do
        if [[ $created_panes -eq $panes ]]; then
            break 2
        fi
        tmux split-window -h
        tmux select-layout tiled
        created_panes=$(( created_panes + 1 ))
    done
    if [[ $created_panes -eq $panes ]]; then
        break
    fi
    tmux split-window -v
    tmux select-layout tiled
    created_panes=$(( created_panes + 1 ))
done

# Activate the "venv_skrib" Python virtual environment in each pane
for pane in $(tmux list-panes -t stream -F '#P'); do
    tmux select-pane -t $pane
    tmux send-keys "conda deactivate" C-m
    tmux send-keys "source ./venv_skrib/bin/activate" C-m
    tmux send-keys "cd src" C-m
    tmux send-keys "clear" C-m

done

# Attach to the tmux session
tmux attach-session -t stream
