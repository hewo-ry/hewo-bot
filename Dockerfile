FROM python:3.13-slim-trixie AS builder

# Install UV package manager
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates gcc python3-dev musl-dev git
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"
ENV UV_LINK_MODE=copy

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable --compile-bytecode

# Copy the project into the intermediate image
ADD . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --compile-bytecode

FROM python:3.13-slim-trixie

LABEL maintainer="Max Mecklin <max.mecklin@hewo.fi>"

ADD docker-entrypoint.sh /app/docker-entrypoint.sh

COPY --from=builder --chown=app:app /app/.venv /app/.venv

WORKDIR /app

RUN ["chmod", "+x", "/app/docker-entrypoint.sh"]

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["/app/.venv/bin/main"]
