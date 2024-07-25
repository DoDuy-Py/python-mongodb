from datetime import datetime
from bson import ObjectId
import json

# Hàm tùy chỉnh để chuyển đổi đối tượng không thể serialize thành JSON
def json_serialize(obj):
    if isinstance(obj, (datetime)):
        return obj.isoformat()
    if isinstance(obj, (ObjectId)):
        return str(obj)
    raise TypeError("Type not serializable")


class Base:
    def send_response(self, handler, response):
        handler.send_response(response["statusCode"])
        for key, value in response["headers"].items():
            handler.send_header(key, value)
        handler.end_headers()
        handler.wfile.write(json.dumps(response["body"], default=json_serialize).encode('utf-8'))

from http import HTTPStatus
from requests import Response

CORS_HEADER = {"Access-Control-Allow-Origin": "*"}
CONTENT_TYPE_JSON = {"Content-Type": "application/json"}

class Response:
    @staticmethod
    def ok(body):
        return {
            "statusCode": HTTPStatus.OK,
            "body": body,
            "headers": {**CORS_HEADER, **CONTENT_TYPE_JSON},
        }

    @staticmethod
    def not_found(body):
        return {
            "statusCode": HTTPStatus.NOT_FOUND,
            "body": body,
            "headers": {**CORS_HEADER, **CONTENT_TYPE_JSON},
        }
    
    @staticmethod
    def unauthorized(body):
        return {
            "statusCode": HTTPStatus.UNAUTHORIZED,
            "body": body,
            "headers": {**CORS_HEADER, **CONTENT_TYPE_JSON, **{"WWW-Authenticate": "Bearer"}},
        }

    @staticmethod
    def bad_request(body):
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": body,
            "headers": {**CORS_HEADER, **CONTENT_TYPE_JSON},
        }