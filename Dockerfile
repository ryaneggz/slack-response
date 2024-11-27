# Stage 1: Build stage
FROM python:3.10-slim AS builder

# Set work directory
WORKDIR /app

# Set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy dependencies and requirements files first
COPY requirements.txt .
# COPY constraints.txt .

# Install system dependencies required by spaCy, build tools, and psycopg
RUN apt-get update && apt-get install --no-install-recommends -y \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install uv \
    && uv pip install -v --system --no-cache-dir -r requirements.txt 

# Stage 2: Final stage
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy application from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Start the FastAPI application
CMD ["python", "main.py"] 