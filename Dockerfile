FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy all files first (needed for pyproject.toml to find README.md)
COPY . .

# Install Python dependencies (non-editable for production)
RUN pip install --no-cache-dir .

# Expose port (Railway uses $PORT)
EXPOSE 8000

# Default command (Railway overrides this via railway.toml)
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
