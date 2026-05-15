#!/bin/bash
PID=$(lsof -ti :8443)
if [ -z "$PID" ]; then
    echo "No server running on port 8443"
    exit 0
fi
kill $PID
echo "Server stopped (PID $PID)"
