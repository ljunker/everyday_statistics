#!/bin/bash

# Configuration
HOST=${1:-"http://localhost:45000"}
API_KEY=${2:-"secret"}

echo "Using HOST: $HOST"
echo "Using API_KEY: $API_KEY"
echo "-----------------------------------"

echo "1. Creating 'coffee' event..."
curl -X POST "$HOST/events" \
     -H "Content-Type: application/json" \
     -H "X-API-KEY: $API_KEY" \
     -d '{"type": "coffee", "quality": 8}'
echo -e "\n"

echo "2. Creating 'work' event with timestamp..."
curl -X POST "$HOST/events" \
     -H "Content-Type: application/json" \
     -H "X-API-KEY: $API_KEY" \
     -d '{"type": "work", "timestamp": "2026-01-12T09:00:00Z", "quality": 5}'
echo -e "\n"

echo "3. Creating 'poop' event..."
curl -X POST "$HOST/events" \
     -H "Content-Type: application/json" \
     -H "X-API-KEY: $API_KEY" \
     -d '{"type": "poop"}'
echo -e "\n"

echo "4. Getting timeline for today (2026-01-12)..."
curl -G "$HOST/timeline" \
     -H "X-API-KEY: $API_KEY" \
     --data-urlencode "date=2026-01-12"
echo -e "\n"

echo "5. Getting all 'coffee' events..."
curl -G "$HOST/events" \
     -H "X-API-KEY: $API_KEY" \
     --data-urlencode "type=coffee"
echo -e "\n"

echo "6. Getting stats..."
curl "$HOST/stats" \
     -H "X-API-KEY: $API_KEY"
echo -e "\n"
