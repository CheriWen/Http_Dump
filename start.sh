#!/bin/bash
cd "$(dirname "$0")"
if lsof -i :8443 -sTCP:LISTEN > /dev/null 2>&1; then
    echo "Server already running on port 8443"
    exit 0
fi
nohup python3 server.py > server.log 2>&1 &
sleep 1
echo "Server started. PID: $!"
echo "Web UI: https://localhost:8443"
echo "API:    https://localhost:8443/api/status"
echo ""
echo "To trust the self-signed cert (required for StatusFetch):"
echo "  sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain cert.pem"
