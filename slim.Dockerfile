# Builder stage
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy dependency files first
COPY pyproject.toml uv.lock ./
# Then copy the rest of the application code
COPY . .

# Install dependencies including database drivers
RUN uv sync --frozen --no-dev --all-extras --python 3.11

# Runtime stage
FROM python:3.11-slim AS runtime

# Overridable Node.js version
ARG NODE_VERSION=22
# OpenTelemetry Collector version
ARG OTEL_VERSION=0.96.0
ARG TARGETARCH

RUN set -eux; \
    case "${TARGETARCH:-amd64}" in \
    arm64|aarch64) OTEL_ARCH=arm64 ;; \
    amd64|x86_64|x64) OTEL_ARCH=amd64 ;; \
    *) OTEL_ARCH=amd64 ;; \
    esac; \
    apt-get update && \
    # Install runtime dependencies (no redis-server, no postgres)
    apt-get install -y curl libpq-dev postgresql-client redis-tools && \
    # Install Node.js
    curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - && \
    apt-get install -y nodejs && \
    # Download and install OpenTelemetry Collector
    OTEL_FILENAME="otelcol-contrib_${OTEL_VERSION}_linux_${OTEL_ARCH}.tar.gz"; \
    curl -L "https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v${OTEL_VERSION}/${OTEL_FILENAME}" -o /tmp/otel-collector.tar.gz && \
    tar xzf /tmp/otel-collector.tar.gz -C /usr/local/bin && \
    rm /tmp/otel-collector.tar.gz && \
    mkdir -p /etc/otel && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Add OpenTelemetry Collector configs
COPY otel/otel-collector-config-file.yaml /etc/otel/config-file.yaml
COPY otel/otel-collector-config-clickhouse.yaml /etc/otel/config-clickhouse.yaml
COPY otel/otel-collector-config-signoz.yaml /etc/otel/config-signoz.yaml

# Copy app from builder
COPY --from=builder /app .

# Set environment variables
ENV LETTA_ENVIRONMENT=PROD \
    VIRTUAL_ENV="/app/.venv" \
    PATH="/app/.venv/bin:$PATH"

# Expose Letta port only (no 5432 or 6379)
EXPOSE 8283 4317 4318

# Use existing startup script
CMD ["./letta/server/startup.sh"]
