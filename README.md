# FinPilot

FinPilot is a production-style FastAPI backend for portfolio rebalancing. It includes JWT authentication, PostgreSQL persistence, SQLAlchemy models, Alembic migrations, Docker Compose, and Pytest coverage.

## Architecture

The project separates HTTP, persistence, and business logic:

- `app/main.py` creates the FastAPI app and mounts versioned routes.
- `app/api/` contains dependency injection and route handlers.
- `app/models/` contains SQLAlchemy ORM models and database constraints.
- `app/schemas/` contains Pydantic request and response contracts.
- `app/services/` contains reusable business logic, including the rebalance engine.
- `app/db/` owns engine/session configuration and declarative metadata.
- `alembic/` contains database migration configuration and the initial schema.
- `tests/` verifies authentication, CRUD behavior, and rebalance calculations.

This structure keeps route handlers thin, makes ownership checks explicit, and keeps portfolio math testable without coupling it to HTTP details.

## Features

- User registration and login with JWT bearer tokens
- Authenticated portfolio CRUD
- Holdings CRUD scoped to portfolio ownership
- Target allocation CRUD scoped to portfolio ownership
- Portfolio summary snapshots with total value and current allocation
- Rebalance recommendations with buy/sell/hold actions
- PostgreSQL-ready schema with Alembic migrations
- Docker Compose local environment
- Pytest suite using an isolated SQLite test database

## Local Setup

### Docker Compose

1. Copy the environment template:

```bash
cp .env.example .env
```

2. Start the API and PostgreSQL:

```bash
docker compose up --build
```

3. Open the API docs:

```text
http://localhost:8000/docs
```

The API container runs `alembic upgrade head` before starting Uvicorn.

### Run Without Docker

1. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` from `.env.example` and set `DATABASE_URL` for your local PostgreSQL instance.

4. Apply migrations:

```bash
alembic upgrade head
```

5. Start the app:

```bash
uvicorn app.main:app --reload
```

## Example API Flow

Register:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"investor@example.com\",\"password\":\"strongpassword\"}"
```

Login:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=investor@example.com&password=strongpassword"
```

Use the returned `access_token` as:

```text
Authorization: Bearer <token>
```

Create a portfolio:

```bash
curl -X POST http://localhost:8000/api/v1/portfolios \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Retirement\"}"
```

Add holdings and targets, then request recommendations:

```bash
curl http://localhost:8000/api/v1/portfolios/1/rebalance \
  -H "Authorization: Bearer <token>"
```

## Rebalance Logic

The engine calculates:

- total portfolio market value
- current allocation per symbol
- target value per symbol
- dollar delta required to reach the target
- action: `BUY`, `SELL`, or `HOLD`

Targets must sum to exactly `100`. Symbols that appear only in targets are treated as new positions to buy, and symbols that appear only in holdings are treated as positions with a zero target.

## Tests

Run:

```bash
pytest
```

The tests override the app database dependency and use a disposable SQLite database.

## Production Notes

- Replace `SECRET_KEY` with a long random secret.
- Use managed PostgreSQL backups and connection pooling in production.
- Restrict CORS to trusted frontend origins before exposing publicly.
- Add rate limiting for auth endpoints.
- Add structured logging and request IDs for observability.
- Run migrations as a release step in mature deployment pipelines.
