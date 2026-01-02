#!/usr/bin/env python3
"""Simple HTTP server to serve the frontend."""
import http.server
import socketserver
import os
import sys

def serve_frontend():
    # Change to the client/dist directory
    os.chdir('client/dist')

    PORT = 5173

    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving frontend at http://localhost:{PORT}")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    serve_frontend()