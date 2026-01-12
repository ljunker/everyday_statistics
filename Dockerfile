# Use an official Python image
FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src
RUN mkdir -p instance && chmod 777 instance

ENV PYTHONPATH=/app

CMD ["python", "src/app.py"]
