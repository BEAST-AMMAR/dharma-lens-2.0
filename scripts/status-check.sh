#!/bin/bash
# VidhiChakshu Status Overview Script
echo "===================================================="
echo " VidhiChakshu Services Status Overview"
echo "===================================================="

docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "vidhichakshu|nyayasetu|adalsetu|NAMES" || echo "No VidhiChakshu containers running."
