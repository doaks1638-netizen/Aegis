FROM python:3.12.2-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /push_service

COPY push_service/pyproject.toml push_service/uv.lock ./

RUN uv sync --no-install-project

FROM python:3.12.2-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /rabbitmq_data

COPY --from=builder /push_service/.venv .

COPY push_service/ ./ 
