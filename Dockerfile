FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry

# Copy dependency files
COPY pyproject.toml poetry.lock* /app/

# Install dependencies only (not the project itself)
RUN poetry config virtualenvs.create false && \
    poetry install --only=main --no-root

# Copy source code 
COPY src/ /app/src/

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

USER appuser

# Set default Kafka bootstrap servers for localhost communication
ENV KAFKA_BOOTSTRAP_SERVERS=host.docker.internal:9092

# Default command
CMD ["python", "src/wbe_scraper/__init__.py"] 