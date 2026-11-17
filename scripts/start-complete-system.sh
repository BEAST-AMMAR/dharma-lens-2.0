#!/bin/bash
# Launch Complete VidhiChakshu Ecosystem
set -e

echo "===================================================="
echo " Starting Full VidhiChakshu Ecosystem"
echo "===================================================="

docker-compose -f docker-compose.extended.yml up -d

echo "Waiting for services to stabilize..."
sleep 5

bash scripts/health-check.sh
