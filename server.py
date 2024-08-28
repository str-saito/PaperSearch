import http.server
import os
import sys
from http.server import CGIHTTPRequestHandler
from dotenv import load_dotenv
import cgitb

cgitb.enable() 

load_dotenv()

ROUTING_TABLE = {
    '/register': '/cgi-bin/register.py',
    '/login': '/cgi-bin/login.py',
    '/logout': '/cgi-bin/logout.py',
    '/': '/cgi-bin/papersearch.py',
    '/summarize': '/cgi-bin/summarize.py',
}

class CGIHandler(CGIHTTPRequestHandler):
    def do_GET(self):
        self.route_request()
    
    def do_POST(self):
        self.route_request()

    def route_request(self):
        print(f"Original request path: {self.path}", file=sys.stderr)
        if self.path in ROUTING_TABLE:
            self.path = ROUTING_TABLE[self.path]
            print(f"Routed to: {self.path}", file=sys.stderr)
        elif self.path.startswith('/static/'):
            self.serve_static_file()
            return
        else:
            self.path = '/cgi-bin/notfound.py'
            print(f"Default route: {self.path}", file=sys.stderr)
        
        self.cgi_info = os.path.split(self.path)
        self.run_cgi()
    
    def serve_static_file(self):
        try:
            static_file_path = os.path.join('/app', self.path[1:])
            with open(static_file_path, 'rb') as file:
                self.send_response(200)
                self.send_header("Content-type", self.guess_type(static_file_path))
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_error(404, "File Not Found: {}".format(self.path))
        except Exception as e:
            self.send_error(500, "Server Error: {}".format(str(e)))

if __name__ == "__main__":
    os.chdir('/app')
    host = ("0.0.0.0", 8000)
    httpd = http.server.HTTPServer(host, CGIHandler)
    print("Serving on port 8000", file=sys.stderr)
    httpd.serve_forever()
