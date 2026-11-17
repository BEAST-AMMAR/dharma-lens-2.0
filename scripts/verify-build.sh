#!/bin/bash
# VidhiChakshu Build Verification
set -e

echo "VidhiChakshu - Build Verification"
echo "================================="
echo ""

DOCKER_USER=${DOCKER_HUB_USERNAME:-beast2711}

echo "✓ Frontend Image:"
docker images ${DOCKER_USER}/vidhichakshu-frontend:latest --format "  Repository: {{.Repository}}\n  Tag: {{.Tag}}\n  Size: {{.Size}}"

echo ""
echo "✓ Node Gateway Image:"
docker images ${DOCKER_USER}/vidhichakshu-node:latest --format "  Repository: {{.Repository}}\n  Tag: {{.Tag}}\n  Size: {{.Size}}"

echo ""
echo "✓ Python Engine Image:"
docker images ${DOCKER_USER}/vidhichakshu-python:latest --format "  Repository: {{.Repository}}\n  Tag: {{.Tag}}\n  Size: {{.Size}}"

echo ""
echo "Image Details:"
docker images | grep vidhichakshu || true
