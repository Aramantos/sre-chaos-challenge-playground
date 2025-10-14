#!/bin/bash

# This script ensures that the local tracker is not enabled in production configurations.

# Exit immediately if a command exits with a non-zero status.
set -e

FILES_TO_CHECK=$(find . -name "docker-compose.prod.yml" -o -path "./k8s/*.yml" -o -path "./k8s/*.yaml")

for file in $FILES_TO_CHECK; do
    if grep -q "ENABLE_LOCAL_TRACKER=true" "$file"; then
        echo "❌ Error: ENABLE_LOCAL_TRACKER=true found in $file"
        exit 1
    fi
done

echo "✅ No production configurations enable the local tracker."