#!/bin/bash
set -e

echo ""
echo "=============================================="
echo "  SOVEREIGN INTELLIGENCE PLATFORM"
echo "  PRIMERS S-FORM SOS — On-Premise Installer"
echo "  v2.5.0 | Lagos, Nigeria Theater"
echo "=============================================="
echo ""

# Check dependencies
command -v docker >/dev/null 2>&1 || { echo "[ERROR] Docker not found. Install Docker first: https://docs.docker.com/get-docker/"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "[ERROR] Docker Compose not found."; exit 1; }

echo "[OK] Docker detected: $(docker --version)"
echo "[OK] Docker Compose detected: $(docker-compose --version)"
echo ""

# Create model directory
mkdir -p ./models
echo "[OK] Model directory ready at ./models"
echo "     Place model weight files here before running for full inference."
echo ""

# Environment setup
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[OK] Environment file created from template."
    echo "     Edit .env to configure operator credentials before first launch."
else
    echo "[OK] Environment file found."
fi

echo ""
echo "[BUILDING] Sovereign Intelligence containers..."
docker-compose build --no-cache

echo ""
echo "[DEPLOYING] Starting sovereign services..."
docker-compose up -d

echo ""
echo "[VERIFYING] Waiting for health check..."
sleep 8

STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ || echo "000")
if [ "$STATUS" = "200" ]; then
    echo "[OK] Backend is LIVE at http://localhost:8000"
else
    echo "[WARN] Backend health check returned $STATUS — check logs: docker-compose logs sip-backend"
fi

echo ""
echo "=============================================="
echo "  DEPLOYMENT COMPLETE"
echo ""
echo "  Dashboard : http://localhost:3000"
echo "  API       : http://localhost:8000"
echo "  API Docs  : http://localhost:8000/docs"
echo ""
echo "  Default credentials:"
echo "  admin    / sip-admin-2024    [L3 TOP SECRET]"
echo "  analyst  / sip-analyst-2024  [L2 SECRET]"
echo "  operator / sip-operator-2024 [L1 RESTRICTED]"
echo ""
echo "  IMPORTANT: Change all credentials before"
echo "  operational deployment."
echo "=============================================="
echo ""
