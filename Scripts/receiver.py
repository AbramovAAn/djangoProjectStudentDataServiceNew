from http.server import BaseHTTPRequestHandler, HTTPServer
class H(BaseHTTPRequestHandler):
    def do_POST(self):
        ln = int(self.headers.get('Content-Length','0'))
        body = self.rfile.read(ln).decode('utf-8')
        print("\n-- WEBHOOK --", self.path)
        print(self.headers)
        print(body)
        self.send_response(200); self.end_headers()
HTTPServer(('127.0.0.1', 9000), H).serve_forever()