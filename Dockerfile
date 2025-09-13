FROM ghcr.io/astral-sh/uv:python3.12-alpine
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PATH="/chat/.venv/bin:$PATH" \
    PYTHONPATH="/chat/:$PYTHONPATH"
WORKDIR /chat
COPY ./pyproject.toml ./uv.lock ./
RUN apk add --no-cache curl && \
    uv sync --locked
COPY ./src/ ./
CMD ["python", "app/main.py"]
