# Crypto Price Tracker

Real-time cryptocurrency price feed using FastAPI WebSockets and Binance live stream.

## Overview

Connects to the Binance WebSocket ticker stream, persists live price data to PostgreSQL, and broadcasts updates to all connected clients in real time.

## Tech Stack

- **FastAPI** — WebSocket server
- **PostgreSQL + SQLAlchemy** — data persistence
- **Alembic** — database migrations
- **websockets** — Binance stream consumer
- **structlog** — structured logging
- **Docker** — containerised deployment

## Getting Started

```bash
# 1. Configure
cp .env.example .env   # set DATABASE_URL and SECRET_KEY

# 2. Start
docker compose up --build
```

> Migrations run automatically on container startup via `entrypoint.sh`.

## Endpoints

| Method    | Path         | Description                        |
|-----------|--------------|------------------------------------|
| GET       | `/`          | Health check                       |
| WebSocket | `/ws/crypto` | Live price feed (JSON broadcast)   |

On WebSocket connect, the client receives a snapshot of current prices followed by live updates.

```json
[
  {
    "symbol": "BTCUSDT",
    "last_price": "67432.12",
    "24_hour_change_percent": "1.82",
    "timestamp": "2026-03-28T10:00:00+00:00"
  }
]
```

## Project Structure

```
app/
├── main.py              # FastAPI app and WebSocket endpoint
├── database.py          # DB engine and session
├── settings.py          # Environment config
├── models/models.py     # ORM models
└── service/
    └── crypto_service.py  # Binance stream consumer
alembic/                 # Migrations
Dockerfile
docker-compose.yml
```

## Environment Variables

```
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/dbname
SECRET_KEY=your-secret-key
```
