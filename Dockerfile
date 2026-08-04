# Dockerfile for Ottoman Agent Pipeline

# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY pyproject.toml .
COPY README.md .

# Install package
RUN pip install --no-cache-dir --prefix=/install -e .

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy from builder
COPY --from=builder /install /usr/local
COPY --from=builder /app/src ./src
COPY --from=builder /app/pyproject.toml .
COPY --from=builder /app/README.md .

# Create data directory
RUN mkdir -p /app/data/sessions
RUN chown -R 1000:1000 /app/data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "ottoman_agent_pipeline.api.server:create_app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
