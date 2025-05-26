# Use Python 3.13 slim image as base
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY src/ src/
COPY main.py .
COPY tests/ tests/

# Install Python dependencies
RUN pip install --no-cache-dir .

# Expose port
EXPOSE 5000

# Default: Run the application
CMD ["python", "main.py"]

# To run tests in Docker:
# docker build -t fit-app .
# docker run --rm fit-app pytest -v 