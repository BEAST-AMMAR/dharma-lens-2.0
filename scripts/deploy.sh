#!/bin/bash
# VidhiChakshu Deployment Script
set -e

echo "===================================================="
echo " Deploying VidhiChakshu Production Services"
echo "===================================================="

if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
fi

echo "[1/2] Stopping existing containers..."
docker-compose down --remove-orphans || true

echo "[2/2] Launching updated VidhiChakshu service stack..."
docker-compose up -d

echo "===================================================="
echo " VidhiChakshu Deployment Complete!"
echo " Web UI: http://localhost:8080"
echo " API Gateway: http://localhost:3000"
echo " ML Engine: http://localhost:8000"
echo "===================================================="
