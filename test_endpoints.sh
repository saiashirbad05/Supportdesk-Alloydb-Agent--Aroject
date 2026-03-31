#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-https://supportdesk-nl-api-260584325793.us-central1.run.app}"

echo "Testing service: ${BASE_URL}"
echo

echo "[1/5] Root"
curl -s "${BASE_URL}/" | python3 -m json.tool
echo

echo "[2/5] Health"
curl -s "${BASE_URL}/health" | python3 -m json.tool
echo

echo "[3/5] Payments Open"
curl -s "${BASE_URL}/demo/payments-open" | python3 -m json.tool
echo

echo "[4/5] Unresolved by Service"
curl -s "${BASE_URL}/demo/unresolved-by-service" | python3 -m json.tool
echo

echo "[5/5] Critical Auth"
curl -s "${BASE_URL}/demo/critical-auth" | python3 -m json.tool
