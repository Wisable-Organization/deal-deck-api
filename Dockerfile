# Use Python 3.10 slim image as base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Configure Poetry: Install to system Python (no virtual env)
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Install dependencies to system Python
RUN poetry install --no-dev --no-root && rm -rf $POETRY_CACHE_DIR

# Copy application code
COPY api/ ./api/

# Expose port
EXPOSE 8000

# Set default port (App Runner sets PORT env var)
ENV PORT=8000

# Run the application (uvicorn is installed to system Python)
# Use sh -c to expand PORT environment variable
CMD sh -c "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"

