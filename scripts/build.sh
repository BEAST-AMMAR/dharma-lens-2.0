#!/bin/bash
# VidhiChakshu Production Container Build Script
set -e

echo "===================================================="
echo " Building VidhiChakshu Production Docker Images"
echo "===================================================="

DOCKER_USER=${DOCKER_HUB_USERNAME:-beast2711}

echo "[1/3] Building Frontend Container..."
docker build -t ${DOCKER_USER}/vidhichakshu-frontend:latest -t ${DOCKER_USER}/vidhichakshu-frontend:v3.0.0 .

echo "[2/3] Building Node API Gateway Container..."
docker build -t ${DOCKER_USER}/vidhichakshu-node:latest -t ${DOCKER_USER}/vidhichakshu-node:v3.0.0 ./node_backend

echo "[3/3] Building Python ML Engine Container..."
docker build -t ${DOCKER_USER}/vidhichakshu-python:latest -t ${DOCKER_USER}/vidhichakshu-python:v3.0.0 ./python_backend

echo "===================================================="
echo " All VidhiChakshu containers built successfully!"
echo "===================================================="
