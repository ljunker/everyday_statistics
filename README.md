# Everyday Statistics Service

![Build Status](https://github.com/ljunker/everyday_statistics/actions/workflows/docker-publish.yml/badge.svg)
![License](https://img.shields.io/github/license/ljunker/everyday_statistics)
![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)
![Coverage](https://img.shields.io/badge/coverage-96%25-brightgreen)

A tiny Flask + SQLite service to track everyday events — like when you poop!  
Built for fun, stats, and easy expansion. Containerized with Docker Compose using a highly optimized, multi-stage Alpine-based image (~85MB).

---

**WARNING: This project is under active development**

This service is experimental and may change or break at any time.  
It is **not stable for production use yet** — expect breaking changes, bugs, and incomplete features.

Use it at your own risk and always back up your data!

---

## Getting Started

### Setup & Start

The easiest way to get started is to use the `setup.sh` script. It will create your `.env` file, generate random API keys, initialize the database, and start the services.

```bash
git clone git@github.com:ljunker/everyday_statistics.git everyday_statistics
cd everyday_statistics
./setup.sh
```

After the script finishes, it will display your `APP_API_KEY`. You can then access the dashboard at `http://localhost:45000`.

---

### Manual Setup (Alternative)

If you prefer to set up the project manually without the `setup.sh` script, follow these steps:

#### **Step A: Clone the repository**
```bash
git clone git@github.com:ljunker/everyday_statistics.git everyday_statistics
cd everyday_statistics
```

#### **Step B: Configure environment variables**
Copy the example environment file and edit it with your desired keys:
```bash
cp dbconn.env.example dbconn.env
```
Open `dbconn.env` and set your own secure values for:
- `APP_API_KEY`: Your main secret key for accessing the API and Dashboard.
- `FLASK_SECRET_KEY`: Used by Flask for session signing.
- `PROMETHEUS_API_KEY`: Used to protect the `/metrics` endpoint.

You can generate good secret keys with:
```bash
openssl rand -hey 32
```

#### **Step C: Build and start the containers**
Use the provided `upgrade.sh` script to build the image and initialize the database tables:
```bash
./upgrade.sh
```

*Or, if you want to do it purely via Docker commands:*
```bash
docker compose up --build -d
docker compose exec web python3 -c "from src.app import app; from src.db import db; with app.app_context(): db.create_all()"
```

#### **Step D: Access the application**
- **Dashboard**: [http://localhost:45000](http://localhost:45000) (Login with your `APP_API_KEY`)
- **API**: [http://localhost:45000/events](http://localhost:45000/events) (Requires `X-API-KEY` header)
- **Metrics**: [http://localhost:45000/metrics](http://localhost:45000/metrics) (Requires `X-API-KEY` header with `PROMETHEUS_API_KEY`)

---

## Authentication

All API requests must include the `X-API-KEY` header.

Example header:
```
X-API-KEY: your_app_api_key
```

Note: The `/metrics` endpoint requires the `PROMETHEUS_API_KEY` in the `X-API-KEY` header instead.

---

## Example API Usage

Replace `your_app_api_key` with your actual `APP_API_KEY`.

**Record an event:**

```bash
curl -X POST http://localhost:45000/events \
     -H "Content-Type: application/json" \
     -H "X-API-KEY: your_app_api_key" \
     -d '{"type": "poop"}'
```

**Get stats:**

```bash
curl http://localhost:45000/stats \
     -H "X-API-KEY: your_app_api_key"
```

---

## Common Commands

**Force rebuild everything:**

```bash
docker compose up --build --force-recreate --remove-orphans
```

**Run local security scan:**

To scan the Docker image for vulnerabilities using Trivy:

```bash
./scan_image.sh
```

This script will build the image and run a scan for `HIGH` and `CRITICAL` vulnerabilities. If you don't have Trivy installed locally, it will automatically run it via Docker.

---

## Testing

To run the tests and see the coverage report:

```bash
./run_tests.sh
```

Or manually:

```bash
pip install -r requirements-dev.txt
python3 -m pytest --cov=src --cov-report=term-missing
```

---

## Tips

- Keep your `.env` out of version control (`.gitignore` it!).
- For production, consider using Docker secrets for API keys.

---
