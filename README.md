# Everyday Statistics Service 🚽📊

A tiny Flask + PostgreSQL service to track everyday events — like when you poop!  
Built for fun, stats, and easy expansion. Containerized with Docker Compose.

---

## 🚀 Getting Started

### 1️⃣ Clone the repo

```bash
git clone git@github.com:ljunker/everyday_statistics.git everyday_statistics
cd everyday_statistics
```

---

### 2️⃣ Create your `.env`

Copy the `dbconn.env.example` to `dbconn.env`:

```bash
cp dbconn.env.example dbconn.env
```
Configure the postgres user, password and db to anything you like (but make it secure ffs...).
The `DATABASE_URL` and `API_KEY` is for the flask server. For the API key, you can use a strong random key generator like `openssl`:

```bash
openssl rand -hex 32
```

---

### 3️⃣ Initialize the database

Before first run, create the tables:

```bash
docker-compose run web flask shell
```

Inside the Flask shell:

```python
from app import db
db.create_all()
exit()
```

### 4️⃣ Build & start services

Use Docker Compose to build and run everything:

```bash
docker-compose up --build
```

Add `-d` to run in detached mode (background).

This starts:
- `db` → PostgreSQL database
- `web` → Flask app

---

## 🔑 Authentication

All requests must include the `X-API-KEY` header. (The one you generated with `openssl`)

Example header:
```
X-API-KEY: supersecretkey
```

---

## 🧪 Example API Usage

**Record an event:**

```bash
curl -X POST http://localhost:5000/events   -H "Content-Type: application/json"   -H "X-API-KEY: supersecretkey"   -d '{"type": "poop"}'
```

**Get stats:**

```bash
curl http://localhost:5000/stats   -H "X-API-KEY: supersecretpoopkey"
```

---

## ⚙️ Common Commands

🔄 **Force rebuild everything:**

```bash
docker compose up --build --force-recreate --remove-orphans
```

---

## 💡 Tips

✅ Keep your `.env` out of version control (`.gitignore` it!).
✅ For production, consider using Docker secrets for API keys.  

---
