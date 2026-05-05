from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading

class MockHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        q = params.get('q', [''])[0]
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        if self.path.startswith('/html_vuln'):
            html = f"<html><body>{q}</body></html>"
        elif self.path.startswith('/html_safe'):
            html = f"<html><body>{q.replace('<', '&lt;').replace('>', '&gt;')}</body></html>"
        elif self.path.startswith('/attr_vuln'):
            html = f"<html><input value=\"{q}\"></html>"
        elif self.path.startswith('/attr_safe'):
            html = f"<html><input value=\"{q.replace('\"', '&quot;')}\"></html>"
        elif self.path.startswith('/js_vuln'):
            html = f"<html><script>var x = \"{q}\";</script></html>"
        elif self.path.startswith('/js_safe'):
            safe_q = q.replace('"', '\\"').replace('<', '\\x3c').replace('>', '\\x3e')
            html = f"<html><script>var x = \"{safe_q}\";</script></html>"
        else:
            html = "<html><body>Unknown endpoint</body></html>"
            
        self.wfile.write(html.encode('utf-8'))

    def log_message(self, format, *args):
        pass

def start_mock_server(port=8080):
    server = HTTPServer(('localhost', port), MockHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server
