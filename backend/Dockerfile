FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .

EXPOSE 5000

CMD ["sh", "-c", "uv run alembic upgrade head && uv run gunicorn --bind 0.0.0.0:5000 app.main:app"]