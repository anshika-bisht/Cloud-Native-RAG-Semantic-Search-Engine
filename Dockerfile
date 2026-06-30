# ---------------------------------------------------------
# Stage 1: Builder
# ---------------------------------------------------------
FROM python:3.12-slim AS builder

# Set environment variables for build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies (leverage Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------
# Stage 2: Runner
# ---------------------------------------------------------
FROM python:3.12-slim AS runner

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies only (libpq5 required for psycopg2/asyncpg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and group
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Create required application directories and set ownership
RUN mkdir -p data uploads logs && \
    chown -R appuser:appgroup /app/data /app/uploads /app/logs

# Copy application source code
COPY --chown=appuser:appgroup . .

# Ensure entrypoint script is executable
RUN chmod +x entrypoint.sh

# Switch to the non-root user
USER appuser

# Expose API port
EXPOSE 8000

# Set entrypoint to run migrations then start the server
ENTRYPOINT ["./entrypoint.sh"]

# Default command (can be overridden by docker-compose)
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
