FROM python:3.13-alpine AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.13-alpine

WORKDIR /app

COPY --from=builder /install /usr/local

COPY src/ ./src
RUN mkdir -p instance && chmod 777 instance

ENV PYTHONPATH=/app

CMD ["python", "src/app.py"]