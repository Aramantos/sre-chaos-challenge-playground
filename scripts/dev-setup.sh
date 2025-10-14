#!/bin/bash

# Add a delay to give the Docker daemon time to start
sleep 10

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Build and Start Services ---
echo "Building all Docker images..."
docker-compose build --no-cache

echo "Starting all services..."
docker-compose up -d

# --- Smoke Tests ---
echo "Running smoke tests..."

# Check that all containers are running
EXPECTED_CONTAINERS=("backend" "local-tracker-service" "frontend" "local-tracker-app" "url-anvil" "prometheus" "grafana" "load-generator" "db" "pgadmin")
for container in "${EXPECTED_CONTAINERS[@]}"; do
    if [ "$(docker-compose ps -q $container)" == "" ] || [ "$(docker-compose ps -q $container | xargs docker inspect -f '{{.State.Status}}')" != "running" ]; then
        echo "❌ Smoke test failed: Container $container is not running."
        exit 1
    fi
done
echo "✅ All containers are running."

# Check local-tracker-app accessibility
if ! curl -s http://localhost:8082 > /dev/null; then
    echo "❌ Smoke test failed: local-tracker-app is not accessible."
    exit 1
fi
echo "✅ local-tracker-app is accessible."

# Add a short delay to allow the Docker network to stabilize
sleep 5

# Run a quick load test
python3 load-generator/load_test.py http://url-anvil:8080 10
echo "✅ Load test completed."

# --- Validate Tracker Isolation ---
echo "Validating tracker isolation..."
bash scripts/enforce_local_tracker_bounds.sh
echo "✅ Tracker isolation validated."

# --- Golden Path Test ---
echo "Running golden path test..."
# Check for the warning message in the local-tracker-service logs
docker-compose logs local-tracker-service | grep "⚠️  WARNING: This is a local-only service for personal tracking and is NOT for official competition scoring. ⚠️" || {
  echo "❌ Golden path test failed: Local Tracker warning not found in logs!"
  exit 1
}
echo "✅ Golden path test passed."

echo "
🎉 Dev setup completed successfully! 🎉"
