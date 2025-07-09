# Everyday Statistics Service 🚽📊

⚠️ **WARNING: This project is under active development**

This service is experimental and may change or break at any time.  
It is **not stable for production use yet** — expect breaking changes, bugs, and incomplete features.

Use it at your own risk and always back up your data!

---

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
The `DATABASE_URL` `PROMETHEUS_SECRET_KEY` and `FLASK_SECRET_KEY` are for the flask server. Generate a good secret key with:

```bash
openssl rand -hex 32
```

Then copy the generated key into your `.env` file as `FLASK_SECRET_KEY`.

---

### 3️⃣ Initialize the database

Before first run, create the tables:

```bash
docker compose run web flask shell
```

Inside the Flask shell:

```python
from app import db
db.create_all()
exit()
```

Then create an admin user with

```bash
docker compose run web flask create-admin
```

You can create additional users later via the web app.

### 4️⃣ Build & start services

Use Docker Compose to build and run everything:

```bash
docker compose up --build
```

Add `-d` to run in detached mode (background).

This starts:
- `db` → PostgreSQL database
- `web` → Flask app

---

## 🔑 Authentication

All requests must include the `X-API-KEY` header. It will be generated when you create a user.

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
curl http://localhost:5000/stats   -H "X-API-KEY: supersecretkey"
```

---

## ⚙️ Common Commands

🔄 **Force rebuild everything:**

```bash
docker compose up --build --force-recreate --remove-orphans
```

---

## 💡 Tips

- ✅ Keep your `.env` out of version control (`.gitignore` it!).
- ✅ For production, consider using Docker secrets for API keys.  

---
