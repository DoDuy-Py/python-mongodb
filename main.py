from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
import threading
from routers import route_request
import json
import os

from views_func.function import init_db
from views_func.shared_func import init_schedule

class RequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/static') or self.path.startswith('/media'):
            self.path = self.path.lstrip('/')
            if os.path.exists(self.path) and os.path.isfile(self.path):
                return super().do_GET()
        else:
            handler_function, param = route_request(self.path, "GET")
            if handler_function:
                if param:
                    handler_function(self, param)
                else:
                    handler_function(self)
            else:
                response = {
                    "statusCode": 404,
                    "body": {"error": "Not Found"},
                    "headers": {"Content-Type": "application/json"}
                }
                self.send_response(response["statusCode"])
                for key, value in response["headers"].items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(json.dumps(response["body"]).encode('utf-8'))

    def do_POST(self):
        handler_function, param = route_request(self.path, "POST")
        if handler_function:
            if param:
                handler_function(self, param)
            else:
                handler_function(self)
        else:
            response = {
                "statusCode": 404,
                "body": {"error": "Not Found"},
                "headers": {"Content-Type": "application/json"}
            }
            self.send_response(response["statusCode"])
            for key, value in response["headers"].items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(json.dumps(response["body"]).encode('utf-8'))
    
    def do_PUT(self):
        handler_function, param = route_request(self.path, "PUT")
        if handler_function:
            if param:
                handler_function(self, param)
            else:
                handler_function(self)
        else:
            response = {
                "statusCode": 404,
                "body": {"error": "Not Found"},
                "headers": {"Content-Type": "application/json"}
            }
            self.send_response(response["statusCode"])
            for key, value in response["headers"].items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(json.dumps(response["body"]).encode('utf-8'))
    
    def do_DELETE(self):
        handler_function, param = route_request(self.path, "DELETE")
        if handler_function:
            if param:
                handler_function(self, param)
            else:
                handler_function(self)
        else:
            response = {
                "statusCode": 404,
                "body": {"error": "Not Found"},
                "headers": {"Content-Type": "application/json"}
            }
            self.send_response(response["statusCode"])
            for key, value in response["headers"].items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(json.dumps(response["body"]).encode('utf-8'))

def run(server_class=HTTPServer, port=8000):
    try:
        server_address = ('127.0.0.1', port)
        httpd = server_class(server_address, RequestHandler)
        print(f'========= Starting httpd server on port {port} ==========')
        threading.Thread(target=init_schedule).start()
        threading.Thread(target=init_db).start()
        httpd.serve_forever()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    run()