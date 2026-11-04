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

Create the environment file and replace the example database password and service keys:

```powershell
Copy-Item .env.example .env
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

Tests are also executed automatically by GitHub Actions before deployment.
