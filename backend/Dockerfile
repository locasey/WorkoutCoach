# Workout Coach Backend Dockerfile
# Production-ready Python Flask application container

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Flask configuration
    FLASK_ENV=production \
    # Port for the application
    PORT=5000

# Install system dependencies
# psycopg2-binary requires libpq-dev on some systems
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" || exit 1

# Run with gunicorn for production
# - Workers: 2-4 recommended for most use cases
# - Timeout: 120s for LLM requests
# - Bind to 0.0.0.0 to accept connections from outside container
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
