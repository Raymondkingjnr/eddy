FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Venv lives outside /app so the ../backend bind mount cannot hide it
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .

EXPOSE 8000

# Apply migrations, then start the dev server with reload
CMD ["sh", "-c", "alembic upgrade head && fastapi dev main.py --host 0.0.0.0 --port 8000"]