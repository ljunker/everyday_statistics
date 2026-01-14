#!/bin/bash

docker compose up --build --force-recreate --remove-orphans -d
# For SQLite, the database will be created automatically if it doesn't exist
# We use flask shell to ensure the tables are created if starting fresh
docker compose exec web python3 -c "
from src.app import app
from src.db import db
with app.app_context():
    db.create_all()
"
