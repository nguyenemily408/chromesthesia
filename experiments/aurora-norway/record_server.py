# Local helper for filming the aurora page: serves this folder and saves a clip the page sends back.
# Run:  python3 record_server.py   (then open http://localhost:8769/aurora.html?audio=<song>&ui=0&record=45)
import http.server, os, urllib.parse
class H(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        name = os.path.basename(urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get('name', ['clip.bin'])[0])
        data = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        open(name, 'wb').write(data)
        self.send_response(200); self.end_headers(); self.wfile.write(b'ok')
    def log_message(self, *a): pass
http.server.ThreadingHTTPServer(('127.0.0.1', 8769), H).serve_forever()
