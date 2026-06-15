# Multi-stage build for production
# Render.com targets the 'production' stage automatically via dockerCommand override

# Stage 1: Base
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Development
FROM base as development

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run with auto-reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage 3: Production
FROM base as production

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Copy startup script and make it executable
COPY --chown=appuser:appuser render_start.sh .
RUN chmod +x render_start.sh

# Expose port (Render uses PORT env var)
EXPOSE 8000

# Run via render_start.sh (migrations + celery bg + uvicorn)
CMD ["bash", "render_start.sh"]
