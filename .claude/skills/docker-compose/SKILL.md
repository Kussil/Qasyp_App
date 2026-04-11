---
name: docker-compose
description: Generate and maintain Docker Compose configuration for Qasyp App's local development environment. Use when setting up services, adding a new service, changing ports or environment variables, or troubleshooting the local stack.
---

# Docker Compose

Generates and maintains the `docker-compose.yml` for Qasyp App's local development environment. Covers all services in the stack: FastAPI, PostgreSQL, Redis, Qdrant, and Celery.

## When to Use

- Setting up the local development environment for the first time
- Adding a new service to the stack (e.g. a new worker, a monitoring tool)
- Changing environment variables or port mappings
- Troubleshooting a service that will not start
- Generating a `docker-compose.override.yml` for local customisation

---

## Service Topology

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   FastAPI   │────▶│ PostgreSQL  │     │    Redis    │
│  (api:8000) │     │  (db:5432)  │     │ (redis:6379)│
└─────────────┘     └─────────────┘     └─────────────┘
       │                                       │
       │                               ┌───────┴────────┐
       │                               │ Celery Worker  │
       │                               │ (background)   │
       │                               └────────────────┘
       │
       ▼
┌─────────────┐
│   Qdrant    │
│ (qdrant:6333│
│  /6334 gRPC)│
└─────────────┘
```

---

## docker-compose.yml

```yaml
version: "3.9"

services:

  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: qasyp_api
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgresql+asyncpg://qasyp:qasyp@db:5432/qasyp_dev
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_URL=http://qdrant:6333
      - SECRET_KEY=${SECRET_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - ENVIRONMENT=development
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
      qdrant:
        condition: service_started
    networks:
      - qasyp_network

  db:
    image: postgres:16-alpine
    container_name: qasyp_db
    environment:
      POSTGRES_USER: qasyp
      POSTGRES_PASSWORD: qasyp
      POSTGRES_DB: qasyp_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U qasyp -d qasyp_dev"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - qasyp_network

  redis:
    image: redis:7-alpine
    container_name: qasyp_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - qasyp_network

  qdrant:
    image: qdrant/qdrant:latest
    container_name: qasyp_qdrant
    ports:
      - "6333:6333"   # REST API
      - "6334:6334"   # gRPC
    volumes:
      - qdrant_data:/qdrant/storage
    networks:
      - qasyp_network

  celery_worker:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: qasyp_celery
    command: celery -A app.tasks.celery_app worker --loglevel=info --queues=embeddings,outreach
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgresql+asyncpg://qasyp:qasyp@db:5432/qasyp_dev
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_URL=http://qdrant:6333
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - ENVIRONMENT=development
    depends_on:
      - redis
      - db
      - qdrant
    networks:
      - qasyp_network

  celery_beat:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: qasyp_celery_beat
    command: celery -A app.tasks.celery_app beat --loglevel=info
    volumes:
      - .:/app
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql+asyncpg://qasyp:qasyp@db:5432/qasyp_dev
    depends_on:
      - redis
    networks:
      - qasyp_network

volumes:
  postgres_data:
  redis_data:
  qdrant_data:

networks:
  qasyp_network:
    driver: bridge
```

---

## .env.example

Commit this file. Never commit `.env` itself.

```dotenv
# Application
SECRET_KEY=change-me-to-a-random-64-char-string
ENVIRONMENT=development

# AI
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Database (overridden by docker-compose for local dev)
DATABASE_URL=postgresql+asyncpg://qasyp:qasyp@localhost:5432/qasyp_dev

# Redis
REDIS_URL=redis://localhost:6379/0

# Vector store
QDRANT_URL=http://localhost:6333
```

---

## Common Commands

```bash
# Start all services
docker compose up -d

# View logs for a specific service
docker compose logs -f api
docker compose logs -f celery_worker

# Restart a single service after a code change
docker compose restart api

# Open a shell inside the API container
docker compose exec api bash

# Run database migrations
docker compose exec api alembic upgrade head

# Run tests inside the container
docker compose exec api pytest --cov=app

# Stop and remove all containers and volumes (full reset)
docker compose down -v

# Rebuild after Dockerfile changes
docker compose up -d --build
```

---

## Environment Variables Reference

| Variable              | Required | Description                              |
|-----------------------|----------|------------------------------------------|
| `SECRET_KEY`          | Yes      | JWT signing key — random 64-char string  |
| `ANTHROPIC_API_KEY`   | Yes      | Claude API key for LLM calls             |
| `DATABASE_URL`        | Yes      | Async PostgreSQL connection string        |
| `REDIS_URL`           | Yes      | Redis connection string                  |
| `QDRANT_URL`          | Yes      | Qdrant REST endpoint                     |
| `ENVIRONMENT`         | Yes      | `development`, `staging`, or `production`|

---

## Rules

- Never hardcode credentials in `docker-compose.yml` — use `${VARIABLE}` syntax
- Always add a `healthcheck` to the `db` service so dependent services wait for it
- Add new services to the `qasyp_network`
- Persist data with named volumes — never anonymous volumes
- Add new required environment variables to `.env.example` immediately
- Do not commit `.env` — add it to `.gitignore`
