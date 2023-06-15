# Chat Printer

Prints the live chat on the screen in a theater

------------

This template needs:

- `Python and requirements.txt`
- `A Pulsar Deamon` -> offered with setup.sh options
- `Minecraft Server` -> offered with setup.sh options
- `A PostgreSQL server` -> offered with setup.sh options

setup.sh options:

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

You need to provide a .env file inside the `src/tools/` folder, with the following values needed:
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `MINECRAFT_IP`
- `MINECRAFT_RCON_PORT`
- `MINECRAFT_RCON_PASSWORD`
- `PULSAR_URL`
- `PULSAR_TOKEN`
- `PULSAR_NAMESPACE`

These are the availables base listeners the dispatcher offers:
- `live.comment`
- `live.join`
- `live.share`
- `live.like`
- `live.gift`
- `live.follow`

You can subscribe any functions to these to receive a profile generated by the function get_profile in `src/tools/sanitize.py`

Please refer to `_template.py` in the same folder to get the boiler plate code to create new stream components.

To send commands to minecraft either use
- `mc.post` -> if you directly send a command without the leading `/`
- `mc.lambda` -> if you send a dill.dumps serialized lambda

Either of these topics can be call/registered and publish/subscribed to.