# --- requirements ---
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir "uvicorn[standard]"

# --- build ---
COPY . .
EXPOSE 8000

# --- uvicorn run ---
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.core.main:app --host 0.0.0.0 --port 8000"]