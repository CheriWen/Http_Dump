#!/bin/bash
SERVER="${1:-https://localhost:8443}"
K="curl -sk"

echo "=== sending samples to $SERVER ==="
echo ""

# GET
$K "$SERVER/api/users"
$K -H "Authorization: Bearer fake-token-123" -H "Accept: application/json" "$SERVER/api/users?page=2&limit=50"

# POST
$K -X POST -H "Content-Type: application/json" \
  -d '{"name":"alice","email":"alice@example.com","role":"admin"}' \
  "$SERVER/api/users"

$K -X POST -H "Content-Type: application/json" \
  -d '{"device":{"id":"mac.local","name":"MacBook","platform":"macOS","os_version":"15.7"},"timestamp":"2026-05-15T10:00:00Z","next_report_in":300,"active_app":{"name":"Xcode","bundle_id":"com.apple.dt.Xcode","mode":"auto"},"media":null}' \
  "$SERVER/api/status"

$K -X POST -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=secret123&remember=true" \
  "$SERVER/login"

# PUT
$K -X PUT -H "Content-Type: application/json" \
  -d '{"name":"bob-updated","role":"editor"}' \
  "$SERVER/api/users/42"

# PATCH
$K -X PATCH -H "Content-Type: application/json" \
  -d '{"status":"archived"}' \
  "$SERVER/api/users/42"

# DELETE
$K -X DELETE "$SERVER/api/users/99"

# HEAD (no body)
$K -I "$SERVER/api/health"

# long body
$K -X POST -H "Content-Type: application/json" \
  -d '{"log":"'"$(python3 -c "print('x'*800)")"'","level":"error","source":"worker-7","trace":"abc123def456ghi789jkl012mno345pqr678stu901vwx234yz56789"}' \
  "$SERVER/api/logs"

# large headers
$K -H "X-Request-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "X-Correlation-ID: 7c9e6679-7425-40de-944b-e07fc1f90ae7" \
  -H "X-Trace: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01" \
  -H "User-Agent: StatusFetch/1.0 (macOS 15.7)" \
  "$SERVER/api/events"

# unsupported method (should still be captured)
$K -X OPTIONS "$SERVER/api/users"

# weird path
$K "$SERVER/deep/nested/./path/../resource?q=hello%20world&sort=desc"

echo ""
echo "=== done ==="
