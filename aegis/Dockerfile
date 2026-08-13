FROM python:3.12.2-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /Aegis

COPY aegis/pyproject.toml aegis/uv.lock ./

RUN uv sync --no-install-project

FROM python:3.12.2-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /Aegis

COPY --from=builder /Aegis/.venv .

COPY aegis/ ./ 
