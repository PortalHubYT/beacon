This template needs:

Python and requirements.txt
A Crossbar router
Minecraft_template
A PostgreSQL server

Tmux.sh options:

- `--install` to install the requirements.txt and eventually update the packages
- `--prune` to prune the docker containers (useful with the next option)
- `--docker` which runs the docker compose for all services
- `--minecraft` which only runs the docker for the minecraft server
- `--pulsar` which only runs the docker for the pulsar queue
- `--postgres` which only runs the docker for the postgres
- `--restart` to stops the dockers in the compose before attempting to run them
- `--run` to automatically run the base components of the template inside the tmux
- `--headless` to not attach to the tmux (useful when testing tmux.sh)

With no options, and by default, the tmux.sh only create a tmux session and split it evenly with 9 tabs

You need to provide a .env file inside the `tools/` folder, with the following values needed:
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_URI`
- `MINECRAFT_IP`
- `MINECRAFT_RCON_PORT`
- `MINECRAFT_RCON_PASSWORD`
- `PULSAR_URL`
- `PULSAR_TOKEN`
- `PULSAR_NAMESPACE`