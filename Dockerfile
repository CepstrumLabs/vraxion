FROM python:3.8-alpine AS builder

LABEL maintainer="Vraxion Development Team" \
      description="Vraxion development environment"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install build dependencies
WORKDIR /build
COPY src/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Build and install the package
COPY src/ .
RUN python setup.py build_ext && \
    python setup.py install

# Final stage
FROM python:3.8-alpine

# Copy installed package from builder
COPY --from=builder /usr/local/lib/python3.8/site-packages/ /usr/local/lib/python3.8/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy tests
COPY tests/ /tests/

# Create non-root user
RUN adduser -D appuser && \
    chown -R appuser:appuser /tests

USER appuser

EXPOSE 8000

WORKDIR /app

CMD ["gunicorn", "-b", "0.0.0.0:8000", "vraxion.app:app"]
