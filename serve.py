#!/usr/bin/env python3
"""CineMatch local server: serves index.html and proxies /graphql to JustWatch (no API key needed).
Usage: python3 serve.py [port]   then open http://localhost:8791"""
import sys, os, urllib.request, urllib.error
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

UPSTREAM = "https://apis.justwatch.com/graphql"
HERE = os.path.dirname(os.path.abspath(__file__))

class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("content-type", ctype)
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.split("?")[0] in ("/", "/index.html"):
            with open(os.path.join(HERE, "index.html"), "rb") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
        else:
            self._send(404, b"not found", "text/plain")

    def do_POST(self):
        if self.path != "/graphql":
            return self._send(404, b"not found", "text/plain")
        n = int(self.headers.get("content-length", 0))
        if n > 20000:
            return self._send(413, b"too large", "text/plain")
        req = urllib.request.Request(UPSTREAM, self.rfile.read(n),
            {"content-type": "application/json", "user-agent": "Mozilla/5.0 CineMatch"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                self._send(r.status, r.read(), "application/json")
        except urllib.error.HTTPError as e:
            self._send(e.code, e.read(), "application/json")
        except Exception as e:
            self._send(502, str(e).encode(), "text/plain")

    def log_message(self, *a): pass

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8791
    print(f"CineMatch running at http://localhost:{port}")
    ThreadingHTTPServer((os.environ.get("HOST","127.0.0.1"), port), H).serve_forever()
