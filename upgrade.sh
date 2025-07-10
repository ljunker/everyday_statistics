#!/bin/bash

docker compose up --build --force-recreate --remove-orphans -d
docker compose run --rm web alembic upgrade head

