# Use an official Python slim image for better security and smaller size
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies if needed (none currently required for SQLite)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     gcc \
#     && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src
RUN mkdir -p instance && chmod 777 instance

ENV PYTHONPATH=/app

CMD ["python", "src/app.py"]
