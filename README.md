# Aegis

## Usage

```bash
git clone https://github.com/doaks1638-netizen/Aegis.git && cd Aegis
mv .env.example .env && vim .env
vim aegis.toml
sudo docker compose up --build
```

## Architecture

![Aegis architecture](./docs/architecture.png)

## Config

```toml
[server]
address = "127.0.0.1:8000" # address where requests are forwarded
rm = '5/m' # default rate limiter (for server and all_path)
rrm = '1/m'
queue=false # True - queued and sent code; False - client will wait; False by default
all_path = true # for routes not listed in the config, use the server settings

[[route]] # use this directive to define a route
path = "/api/v1/products"
rm = "5/m" # how many requests will be accepted
rrm = "1/m" # how many requests will actually reach the server
queue=false 
code=202 # also default code for queue
active = true

[[route]]
path = "/api/v1/users"
rm = "10/m"
rrm = 'server' # if omitted entirely, all requests bypass rrm immediately
active = false # whether to serve this API?
```

## Roadmap

![Aegis roadmap](./docs/roadmap.png)