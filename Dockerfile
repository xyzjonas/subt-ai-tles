FROM node:22-alpine AS frontend
WORKDIR /build
COPY src/app/frontend/package.json ./
RUN npm install
COPY src/app/frontend/ ./
RUN npm run build

FROM python:3.13-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY src/lib src/lib
COPY src/app/pyproject.toml src/app/pyproject.toml
COPY src/app/backend src/app/backend
RUN uv sync --frozen --no-dev --package subt-ai-tles-app

COPY --from=frontend /build/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN rm -f /etc/nginx/sites-enabled/default
COPY docker-entrypoint.sh /docker-entrypoint.sh

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 80
CMD ["/docker-entrypoint.sh"]
