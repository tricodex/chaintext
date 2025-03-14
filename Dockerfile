FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    tpm2-tools \
    libtss2-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install uv
RUN pip install --no-cache-dir uv

# Copy requirements file
COPY requirements.txt /app/

# Install dependencies with --system flag
RUN uv pip install --system --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Create logs directory
RUN mkdir -p logs

# Set permissions for TPM device access if mounted
RUN echo "Will access TPM device at runtime if available"

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "run.py"]
