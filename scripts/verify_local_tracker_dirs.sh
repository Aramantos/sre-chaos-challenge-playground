#!/bin/bash
# Ensures all renamed directories and imports are in sync

grep -R "tracking-service" ./ | grep -v "local-tracker-service" && echo "❌ Found old tracking-service reference!" && exit 1
grep -R "tracking-app" ./ | grep -v "local-tracker-app" && echo "❌ Found old tracking-app reference!" && exit 1
echo "✅ All local tracker names consistent."
