"""
Simple HTTP server to serve local test HTML files
Run this to test the analyzer with local files
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class MyHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

if __name__ == '__main__':
    port = 8080
    print(f"Starting test server on http://localhost:{port}")
    print(f"\nTest URLs:")
    print(f"  Good Example: http://localhost:{port}/test_site_good.html")
    print(f"  Poor Example: http://localhost:{port}/test_site_poor.html")
    print(f"\nPress Ctrl+C to stop the server\n")
    
    server = HTTPServer(('localhost', port), MyHandler)
    server.serve_forever()
