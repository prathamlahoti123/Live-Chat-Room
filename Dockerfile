FROM ghcr.io/astral-sh/uv:python3.12-alpine
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PATH="/app/.venv/bin:$PATH"
WORKDIR /app
COPY ./pyproject.toml ./uv.lock ./
RUN uv sync --locked
COPY ./app/ /app
CMD ["python", "main.py"]
