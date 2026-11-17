#!/bin/bash
# AdalSetu System Health Check Script

echo "===================================================="
echo " Checking AdalSetu Services Status"
echo "===================================================="

check_service() {
    local name=$1
    local url=$2
    local expected=$3

    echo -n "Checking $name ($url)... "
    response=$(curl -s "$url" || echo "FAILED")
    
    if echo "$response" | grep -q "$expected"; then
        echo "OK"
        return 0
    else
        echo "FAILED"
        return 1
    fi
}

check_service "Frontend Presentation Layer" "http://localhost:8080/index.html" "VidhiChakshu"
check_service "Express API Gateway" "http://localhost:3000/health" "VidhiChakshu API Gateway"
check_service "FastAPI Python Engine" "http://localhost:8000/health" "VidhiChakshu AI Engine"

echo "===================================================="
