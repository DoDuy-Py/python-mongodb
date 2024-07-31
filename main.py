from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
import threading
from routers import route_request, rate_limit
import json
import os

from views_func.function import init_db
from views_func.shared_func import init_schedule, logger

class RequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        ### Kiểm tra user_id
        user_id = self.headers.get('User-ID')
        if not user_id:
            self.send_response(400, '{"error": "User-ID header is required"}')
            return
        
        if self.path.startswith('/static') or self.path.startswith('/media'):
            self.path = self.path.lstrip('/')
            if os.path.exists(self.path) and os.path.isfile(self.path):
                return super().do_GET()
        else:
            # Kiểm tra rate limit
            is_allowed, remaining = rate_limit(user_id, "GET", self.path)

            if not is_allowed:
                response = {
                    "statusCode": 429,
                    "body": {"error": f"Rate limit exceeded, remaining {remaining}"},
                    "headers": {"Content-Type": "application/json"}
                }
                self.send_response(response["statusCode"])
                for key, value in response["headers"].items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(json.dumps(response["body"]).encode('utf-8'))
                # self.send_response(429, f'{{"error": "Rate limit exceeded", "remaining": {remaining}}}')
                return
            
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
        server_address = ('0.0.0.0', port)
        httpd = server_class(server_address, RequestHandler)
        logger.info(f'========= Starting httpd server on port {port} ==========')
        threading.Thread(target=init_db).start()
        threading.Thread(target=init_schedule).start()
        httpd.serve_forever()
    except Exception as e:
        logger.error(e)

if __name__ == "__main__":
    run()