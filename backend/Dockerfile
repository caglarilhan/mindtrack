# PRD v2.0 - BIST AI Smart Trader Production Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.production.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.production.txt

# Copy only necessary files
COPY fastapi_main.py .
COPY auth.py .
COPY config.py .
COPY firestore_schema.py .
COPY grey_topsis_ranking.py .
COPY fundamental_analyzer.py .
COPY technical_pattern_engine.py .
COPY ai_ensemble_v2.py .
COPY rl_portfolio_agent.py .
COPY sentiment_xai_engine.py .
COPY real_time_pipeline.py .
COPY websocket_connector.py .
COPY production_test.py .
COPY monitoring/ ./monitoring/

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "fastapi_main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
