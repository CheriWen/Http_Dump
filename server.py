#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template_string
from threading import Lock

app = Flask(__name__)
lock = Lock()
received_data = []

HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>dump</title>
    <style>
        :root {
            --bg: oklch(11% 0.003 80);
            --surface: oklch(14.5% 0.004 80);
            --surface-border: oklch(22% 0.005 80);
            --text: oklch(85% 0.008 85);
            --text-muted: oklch(58% 0.008 85);
            --accent: oklch(68% 0.12 75);
            --accent-dim: oklch(50% 0.06 75);
            --radius: 4px;
        }

        *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: system-ui, -apple-system, sans-serif;
            background: var(--bg);
            color: var(--text);
            padding: 32px 40px;
            min-height: 100vh;
            font-size: 13px;
            line-height: 1.6;
            letter-spacing: 0.01em;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-bottom: 28px;
            padding-bottom: 14px;
            border-bottom: 1px solid var(--surface-border);
        }

        h1 {
            font-size: 15px;
            font-weight: 200;
            color: var(--text);
            letter-spacing: 0.04em;
            text-transform: lowercase;
        }

        .status-row {
            display: flex;
            gap: 24px;
            font-size: 11px;
            color: var(--text-muted);
            letter-spacing: 0.02em;
            font-weight: 350;
        }
        .status-row strong {
            color: var(--text);
            font-weight: 450;
        }

        .toolbar {
            display: flex;
            gap: 6px;
            margin-bottom: 24px;
        }
        .toolbar button {
            font-family: inherit;
            font-size: 11px;
            font-weight: 350;
            letter-spacing: 0.02em;
            color: var(--text-muted);
            background: var(--surface);
            border: 1px solid var(--surface-border);
            border-radius: var(--radius);
            padding: 4px 10px;
            cursor: pointer;
            transition: color 0.1s, border-color 0.1s;
        }
        .toolbar button:hover {
            color: var(--text);
            border-color: var(--accent-dim);
        }

        .empty-state {
            text-align: center;
            padding: 100px 20px;
            color: var(--text-muted);
            font-size: 12px;
            font-weight: 300;
            letter-spacing: 0.02em;
        }
        .empty-state small {
            display: block;
            margin-top: 6px;
            opacity: 0.5;
        }

        .entry {
            background: var(--surface);
            border: 1px solid var(--surface-border);
            border-radius: var(--radius);
            margin-bottom: 8px;
            overflow: hidden;
        }

        .entry-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 12px;
            font-size: 11px;
            letter-spacing: 0.02em;
            border-bottom: 1px solid var(--surface-border);
        }
        .entry-bar .verb {
            font-weight: 500;
            font-size: 10px;
            letter-spacing: 0.03em;
            padding: 1px 6px;
            border-radius: 2px;
        }
        .verb-GET     { background: oklch(20% 0.01 95);  color: oklch(68% 0.08 95); }
        .verb-POST    { background: oklch(16% 0.01 145); color: oklch(60% 0.08 155); }
        .verb-PUT     { background: oklch(18% 0.01 65);  color: oklch(62% 0.08 75); }
        .verb-DELETE  { background: oklch(18% 0.01 25);  color: oklch(55% 0.1 25); }
        .verb-PATCH   { background: oklch(18% 0.01 320); color: oklch(60% 0.06 310); }
        .verb-HEAD    { background: oklch(19% 0.008 250); color: oklch(63% 0.05 270); }
        .verb-OPTIONS { background: oklch(18% 0.01 20);   color: oklch(58% 0.06 30); }
        .entry-bar .path-label {
            margin-left: 10px;
            color: var(--text);
            font-weight: 400;
            font-family: ui-monospace, SFMono, monospace;
            font-size: 11px;
        }
        .entry-bar .stamp {
            color: var(--text-muted);
            font-size: 10px;
            font-weight: 300;
        }

        .entry-body {
            padding: 10px 12px;
        }
        .entry-body pre {
            font-family: ui-monospace, SFMono, monospace;
            font-size: 11px;
            line-height: 1.55;
            color: oklch(82% 0.015 85);
            white-space: pre-wrap;
            word-break: break-all;
            tab-size: 2;
        }
    </style>
</head>
<body>
    <header>
        <h1>dump</h1>
        <div class="status-row">
            <span>received: <strong id="count">0</strong></span>
            <span>last: <strong id="last">--</strong></span>
        </div>
    </header>
    <div class="toolbar">
        <button onclick="loadData(true)">refresh</button>
        <button onclick="clearData()">clear</button>
    </div>
    <div id="content">
        <div class="empty-state">
            listening on all paths
            <small>send requests to https://localhost:8443</small>
        </div>
    </div>
    <script>
        let renderedCount = 0;

        function buildEntry(r, index) {
            let bodyDisplay = '';
            try { bodyDisplay = JSON.stringify(JSON.parse(r.body), null, 2); } catch(e) { bodyDisplay = r.body; }
            const dump = {
                method: r.method,
                path: r.path,
                headers: r.headers,
                body: bodyDisplay,
                received_at: r.received_at
            };
            return '<div class="entry">'
                + '<div class="entry-bar">'
                + '<span><span class="verb verb-' + r.method + '">' + r.method + '</span>'
                + '<span class="path-label">' + esc(r.path) + '</span></span>'
                + '<span class="stamp">' + esc(r.received_at) + '</span>'
                + '</div>'
                + '<div class="entry-body"><pre>' + esc(JSON.stringify(dump, null, 2)) + '</pre></div>'
                + '</div>';
        }

        function fullRebuild(data) {
            let html = '';
            for (let i = data.length - 1; i >= 0; i--) {
                html += buildEntry(data[i], i + 1);
            }
            document.getElementById('content').innerHTML = html
                || '<div class="empty-state">listening on all paths<small>send requests to https://localhost:8443</small></div>';
            renderedCount = data.length;
        }

        async function loadData(forceFull) {
            try {
                const res = await fetch('/api/data');
                const data = await res.json();
                document.getElementById('count').textContent = data.length;
                document.getElementById('last').textContent = data.length > 0
                    ? (data[data.length - 1].received_at || '--') : '--';

                if (data.length === 0) {
                    document.getElementById('content').innerHTML = '<div class="empty-state">listening on all paths<small>send requests to https://localhost:8443</small></div>';
                    renderedCount = 0;
                    return;
                }

                if (forceFull) {
                    fullRebuild(data);
                    return;
                }

                const newCount = data.length - renderedCount;
                if (newCount <= 0) return;

                let html = '';
                for (let i = data.length - 1; i >= renderedCount; i--) {
                    html += buildEntry(data[i], i + 1);
                }
                const content = document.getElementById('content');
                content.insertAdjacentHTML('afterbegin', html);
                renderedCount = data.length;
            } catch(e) { console.error(e); }
        }

        async function clearData() {
            await fetch('/api/data', { method: 'DELETE' });
            document.getElementById('content').innerHTML = '<div class="empty-state">listening on all paths<small>send requests to https://localhost:8443</small></div>';
            document.getElementById('count').textContent = '0';
            document.getElementById('last').textContent = '--';
            renderedCount = 0;
        }

        function esc(str) {
            if (!str) return '';
            if (typeof str === 'object') str = JSON.stringify(str);
            return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
        }

        loadData(true);
        setInterval(() => loadData(false), 2000);
    </script>
</body>
</html>'''


@app.route('/', defaults={'catch_path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
@app.route('/<path:catch_path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
def catch_all(catch_path):
    path = '/' + catch_path if catch_path else '/'

    if request.method == 'GET' and (path == '/' or path == '/api/data'):
        if path == '/':
            return render_template_string(HTML)
        if path == '/api/data':
            with lock:
                return jsonify(list(received_data))

    if request.method == 'DELETE' and path == '/api/data':
        with lock:
            received_data.clear()
        print('[CLEARED]')
        return jsonify({'ok': True})

    body = request.get_data(as_text=True)
    record = {
        'method': request.method,
        'path': path,
        'headers': dict(request.headers),
        'body': body,
        'received_at': datetime.now(timezone.utc).isoformat()
    }
    with lock:
        received_data.append(record)
    print(f'[{record["method"]}] {record["path"]} | body: {body[:100]}{"..." if len(body) > 100 else ""}')
    return jsonify({'ok': True}), 200


if __name__ == '__main__':
    cert_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cert.pem')
    key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'key.pem')

    print('=' * 60)
    print('  Http_Dump')
    print('  https://localhost:8443')
    print('  Accepts any method/path, prints raw data')
    print('=' * 60)
    print()

    app.run(host='0.0.0.0', port=8443, ssl_context=(cert_path, key_path), debug=False)
