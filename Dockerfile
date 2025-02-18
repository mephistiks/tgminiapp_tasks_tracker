FROM python:3.12-slim-bookworm

RUN apt-get update

COPY --from=ghcr.io/astral-sh/uv:0.4.24 /uv /uvx /bin/


WORKDIR /usr/src/code

COPY ../r.txt .

RUN uv pip sync r.txt --system

COPY . .