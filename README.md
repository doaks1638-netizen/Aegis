# Aegis 👑

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.139%2B-00a393.svg)](https://fastapi.tiangolo.com/)
[![Redis](https://img.shields.io/badge/Redis-8.0%2B-dc382d.svg)](https://redis.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ed.svg)](https://www.docker.com/)

**Aegis** is an ergonomic, high-performance API Gateway, Traffic Shaper, and Queuing Reverse Proxy built with Python, FastAPI, and Redis. It acts as a protective shield around your backend, preventing server overload without dropping client requests.

---

## ✨ Features & Two-Stage Traffic Shaping

1. **Client Rate Limiting (`rm`)**: Blocks spam/DDoS requests when client limits are exceeded (HTTP 429).
2. **Backend Rate Throttling (`rrm`)**: Controls the exact speed of requests reaching your target server.
3. **Predictive Load Shedding (`max_wait_time`)**: Rejects requests (HTTP 429) if the estimated queue wait time exceeds a configured threshold.
4. **Circuit Breaker (`max_failures`, `sec_cooldown`)**: Automatically halts traffic (HTTP 503) if the backend returns consecutive 5xx errors.
5. **Redis Queuing (`queue`)**: Queues excess requests in Redis and processes them smoothly at safe backend rates.
   - `queue = true`: **Sync Mode** — connection is held until the backend responds (ideal for AI/LLM & heavy queries).
   - `queue = false`: **Async Mode** — returns `202 Accepted` immediately, worker processes in background (ideal for webhooks).

---

## 🏗️ Architecture

![Aegis architecture](./docs/architecture.png)

---

## 🚀 Quick Start

```bash
git clone https://github.com/doaks1638-netizen/Aegis.git && cd Aegis
mv .env.example .env
sudo docker compose up --build
```

> ⚠️ **Note**: Aegis uses ports `6379` (Redis) and `6378`. Adjust in `docker-compose.yaml` if needed.

---

## ⚙️ Configuration (`aegis.toml`)

Units: `s` (seconds), `m` (minutes), `h` (hours), `d` (days), `y` (years).

```toml
[settings]
address = "127.0.0.1:8000"  # Target backend address
rm = "15/m"                  # Max incoming client requests (rate limit)
rrm = "10/m"                 # Max requests forwarded to backend (rate throttle)
queue = true                 # Default queue mode (true = sync, false = async)
all_path = true              # Fallback for unlisted routes
behind_nginx = false         # Extract IP from X-Real-IP when behind a reverse proxy
max_wait_time = 60.0         # Max queue wait time in seconds (predictive load shedding)
max_failures = 5             # Consecutive 5xx errors to trigger Circuit Breaker
sec_cooldown = 30.5          # Circuit Breaker cooldown duration in seconds

[[route]]
path = "/api/v1/products"
rm = "20/m"
rrm = "5/m"
queue = true
active = true
max_wait_time = 16.05
max_failures = 5
sec_cooldown = 30.5

[[route]]
path = "/api/v1/webhooks"
rm = "100/m"
rrm = "10/m"
queue = false                # Async mode — returns 202 immediately
code = 202
active = true
```

---

## 🌐 Deployment with NGINX

Aegis buffers request payloads in memory before processing/queuing them. To protect Aegis from memory exhaustion when clients upload large files, it is recommended to run NGINX in front of Aegis and restrict payload sizes using `client_max_body_size`.

### Option 1: Using your own NGINX / Reverse Proxy ⚡

If you are using your own NGINX or external reverse proxy:

1. Enable `behind_nginx = true` in `aegis.toml` so Aegis extracts the client IP from HTTP headers:
   ```toml
   [settings]
   behind_nginx = true
   ```
2. In your NGINX configuration, pass the `X-Real-IP` header and limit max body size:
   ```nginx
   client_max_body_size 10m;
   proxy_set_header X-Real-IP $remote_addr;
   ```

### Option 2: Using the built-in NGINX container 📦

An optional pre-configured NGINX setup is included in the project:

1. Set `behind_nginx = true` in `aegis.toml`.
2. Uncomment the `nginx` service in `docker-compose.yaml`.
3. Adjust `client_max_body_size` in `nginx/nginx.conf` if needed (default: `10m`).

---

## 🗺️ Roadmap

![Aegis roadmap](./docs/roadmap.png)

---

## 📄 License

[MIT License](./LICENSE) © 2026 doaks
