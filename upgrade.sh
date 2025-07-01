#!/bin/bash

git pull
docker compose up --build --force-recreate --remove-orphans -d
docker compose run web alembic upgrade head

