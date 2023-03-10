password=$(grep -Po '(?<="rcon_password": ")[^"]*' config.json)
ip=$(grep -Po '(?<="server_ip": ")[^"]*' config.json)

echo $password
echo $ip