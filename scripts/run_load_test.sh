#!/bin/bash

# This script provides a user-friendly way to run load tests against different targets.

# Exit immediately if a command exits with a non-zero status.
set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <target_name> [request_count]"
    echo "Example: $0 url-anvil 100"
    exit 1
fi

TARGET_NAME=$1
REQUEST_COUNT=${2:-10} # Default to 10 requests if not provided

# Determine the target URL
if [ "$TARGET_NAME" == "url-anvil" ]; then
    TARGET_URL="http://url-anvil:8080"
else
    # Assume the target is a contributor app
    TARGET_URL="http://$TARGET_NAME:8080"
fi

# Execute the load test
echo "Running load test against $TARGET_NAME at $TARGET_URL..."
docker-compose exec load-generator python3 load_test.py "$TARGET_URL" "$REQUEST_COUNT"
