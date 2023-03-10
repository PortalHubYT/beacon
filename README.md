This template needs:

Python and requirements.txt
A Crossbar router
Minecraft_template
A PostgreSQL server

Tmux.sh options:

`--install` to install the requirements.txt and eventually update the packages
`--prune` to prune the docker containers (useful with the next option)
`--docker` which runs the docker compose
and `--run` to automatically run the base components of the template

With no options, and by default, the tmux.sh only create a tmux session and split it evenly with 9 tabs