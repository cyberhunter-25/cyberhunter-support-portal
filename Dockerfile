# Multi-stage Dockerfile for CyberHunter Security Portal
# Stage 1: Build stage
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements/ /app/requirements/

# Install Python dependencies
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements/prod.txt

# Stage 2: Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    clamav \
    clamav-daemon \
    clamav-freshclam \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 cyberhunter && \
    mkdir -p /var/www/cyberhunter-portal/uploads && \
    mkdir -p /var/log/cyberhunter-portal && \
    mkdir -p /var/run/clamav && \
    chown -R cyberhunter:cyberhunter /var/www/cyberhunter-portal && \
    chown -R cyberhunter:cyberhunter /var/log/cyberhunter-portal && \
    chown -R clamav:clamav /var/run/clamav

# Set working directory
WORKDIR /app

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements /app/requirements

# Install dependencies
RUN pip install --no-cache /wheels/*

# Copy application code
COPY --chown=cyberhunter:cyberhunter . .

# Copy and set up ClamAV configuration
COPY docker/clamd.conf /etc/clamav/clamd.conf
COPY docker/freshclam.conf /etc/clamav/freshclam.conf

# Copy supervisor configuration
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV UPLOAD_FOLDER=/var/www/cyberhunter-portal/uploads

# Create startup script
RUN echo '#!/bin/bash\n\
# Update ClamAV database\n\
freshclam --quiet\n\
# Start supervisor\n\
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf' > /start.sh && \
chmod +x /start.sh

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run as root for supervisord
# The flask app will run as cyberhunter via supervisord config

# Run the application
CMD ["/start.sh"]