from functools import wraps
import json

from auth.auth_token import validate_token
from core.base import Response
from views_func.function import format_response_data

def permission_required(permissions: list = []):
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            try:
                auth = request.headers.get("Authorization")
                if not auth:
                    response = Response.unauthorized({'message': 'Authorization token not provided'})
                    return self.send_response(request, response)
                
                user = validate_token(auth)
                if not user:
                    response = Response.unauthorized({'message': 'Authorization token not provided'})
                    return self.send_response(request, response)
                
                if isinstance(user, str):
                    user = json.loads(user)
                
                if not any(role in user.get('roles', []) for role in permissions):
                    response = Response.unauthorized({'message': 'Permission denied'})
                    return self.send_response(request, response)

                return func(self, request, *args, **kwargs)
            except Exception as e:
                print(e)
                response = Response.bad_request(format_response_data(400, "An error occurred", None))
                return self.send_response(request, response)
        return wrapper
    return decorator


### FOR CLASS VIEWSET
class PermissionRequired:
    def __init__(self, permissions):
        self.permissions = permissions

    def __call__(self, cls):
        orig_create = cls.create

        def new_create(self, request):
            try:
                auth = request.headers.get("Authorization")
                if not auth:
                    response = Response.unauthorized({'message': 'Authorization token not provided'})
                    return self.send_response(request, response)
                
                user = validate_token(auth)
                if not user:
                    response = Response.unauthorized({'message': 'Authorization token not provided'})
                    return self.send_response(request, response)
                
                if isinstance(user, str):
                    user = json.loads(user)
                
                if not any(role in user.get('roles', []) for role in self.permissions):
                    response = Response.unauthorized({'message': 'Permission denied'})
                    return self.send_response(request, response)

                return orig_create(self, request)
            except Exception as e:
                print(e)
                response = Response.bad_request(format_response_data(400, "An error occurred", None))
                return self.send_response(request, response)

        cls.create = new_create
        return cls