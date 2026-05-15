# httpdump

Catch-all HTTPS server. Records every incoming request and displays raw method, path, headers, and body in a browser.

## Quick start

```
pip install flask
python3 server.py
```

Open https://localhost:8443. Send requests to any path:

```
curl -sk -X POST https://localhost:8443/api/test \
  -H "Content-Type: application/json" \
  -d '{"hello":"world"}'
```

Self-signed certificate at startup. Trust it in your keychain for local use:

```
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain cert.pem
```

## Scripts

| Script | Purpose |
|--------|---------|
| `start.sh` | Start server in background |
| `stop.sh` | Stop background server |
| `send-samples.sh` | Send sample requests across all HTTP methods |

## License

MIT
