#!/bin/bash
docker-compose build --no-cache local-tracker-service local-tracker-app
docker-compose up -d local-tracker-service local-tracker-app
python3 load-generator/load_test.py 10
docker-compose logs local-tracker-service | grep "⚠️  WARNING: This is a local-only service for personal tracking and is NOT for official competition scoring. ⚠️" || {
  echo "❌ Local Tracker warning not found in logs!"
  exit 1
}
echo "✅ Local Tracker validation passed."
