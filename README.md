# Seafi Server

> This project is currently under active development.

**seafi** is a project for convenient housing search in Kyrgyzstan. It collects new rental and real estate listings and sends them to users.

**seafi-server** is a backend part of the project. It provides an API for the project's own client — the Telegram bot [@seafi_arenda_bot](https://t.me/seafi_arenda_bot).

Visit [site](https://seafi.xaris.space/)

Also, see client repository — [seafi-bot](https://github.com/xarisdev/seafi-bot)

## API Documentation

Full interactive API documentation is available through Swagger UI: [Open Swagger UI](https://seafi.xaris.space/docs)

## Architecture

FastAPI Server
    ⇅
Telegram Bot

See detailed API documentation and architecture notes in Russian [here](docs/README.md)

## Stack

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Pydantic
* pytest-asyncio
* Docker

## Running

### Local

The API requires a reachable PostgreSQL database. Create `.env` from the example and set `POSTGRES_URL` to the database address reachable from the host (use `localhost`, not the Compose service name `db`):

```bash
cp .env.example .env
```

Create a virtual environment and install dependencies (Python 3.12, matching the Docker image):

```bash
python -m venv .venv
pip install -r requirements.txt
```
Start the server:

```bash
alembic upgrade head
uvicorn src.core.main:app --reload --port 8000
```

### Docker

Create the environment file and replace the example database password and service keys. The Compose `POSTGRES_URL` must use host `db` because the API connects to the database container over the Compose network.

```bash
cp .env.example .env
```

Then start the API and PostgreSQL:

```bash
docker compose up -d --build
```

## Testing

Run tests locally:

```bash
pytest
```

The current GitHub Actions workflow deploys on pushes to `main`; it does not run the test suite. Tests require PostgreSQL at `localhost:5432` with a database named `seafi_test` and the credentials configured in `tests/conftest.py`.
