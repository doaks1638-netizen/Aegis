# Aegis

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
3. **Redis Queuing (`queue`)**: Queues excess requests in Redis and processes them smoothly at safe backend rates.
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
address = "127.0.0.1:8000" # Target backend address
rm = "15/m"                # Max incoming client requests
rrm = "10/m"               # Max requests forwarded to backend
queue = true               # Default queue mode (sync)
all_path = true            # Fallback for unlisted routes

[[route]]
path = "/api/v1/products"
rm = "20/m"
rrm = "5/m"
queue = true
active = true

[[route]]
path = "/api/v1/webhooks"
rm = "100/m"
rrm = "10/m"
queue = false              # Async mode (returns 202 Accepted)
code = 202
active = true
```

---

## 🗺️ Roadmap

![Aegis roadmap](./docs/roadmap.png)

---

## 📄 License

[MIT License](./LICENSE) © 2026 doaks
) for more information.

Copyright (c) 2026 doaks
