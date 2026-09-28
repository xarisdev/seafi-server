# Seafi Server

> This project is currently under active development.

**seafi** is a project for convenient housing search in Kyrgyzstan. It collects new rental and real estate listings and sends them to users.

**seafi-server** is a backend part of the project. It provides an API for the project's own client — the Telegram bot [@seafi_arenda_bot](https://t.me/seafi_arenda_bot).

## Architecture

Telegram Bot → API → WebAgent → Real Estate Websites

## Stack

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic
* pytest-asyncio
* Docker

## Running

### Local

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
pip install -r requirements.txt
```
Start the server:

```bash
uvicorn src.core.main:app --reload --port 8000
```

### Docker

```bash
docker compose up -d --build
```

## API Documentation

Full interactive API documentation is available through Swagger UI:

**[Open Swagger UI](https://seafi.xaris.space/docs)**

## Testing

Run tests locally:

```bash
pytest
```

Tests are also executed automatically by GitHub Actions before deployment.
