import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import threading

from bson import ObjectId
from auth.auth_token import validate_token
from core.settings import role_collection
from core.base import json_serialize, Base, Response
from views_func.decorator import permission_required
from views_func.function import format_response_data, thread_update_roles_users

class RoleViewSet(Base):

    @permission_required(permissions=['admin'])
    def create(self, request):
        content_length = int(request.headers['Content-Length'])
        post_data = request.rfile.read(content_length).decode('utf-8')
        try:
            role_data = json.loads(post_data)
            result = role_collection.insert_one(role_data)
            role_data["_id"] = str(result.inserted_id)
            response = Response.ok(role_data)
        except Exception as e:
            response = Response.bad_request({"error": str(e)})
        self.send_response(request, response)

    def get(self, request):
        try:
            roles = list(role_collection.find())
            for role in roles:
                role["_id"] = str(role["_id"])
            response = Response.ok(roles)
        except Exception as e:
            response = Response.bad_request({"error": str(e)})
        self.send_response(request, response)
    
    @permission_required(permissions=['admin'])
    def delete(self, request, pk=None):
        try:
            # auth = request.headers.get("Authorization")
            # if not auth:
            #     response = Response.unauthorized({'message': 'Authorization token not provided'})
            #     return self.send_response(request, response)
            
            # user = validate_token(auth)
            # if not user:
            #     response = Response.unauthorized({'message': 'Authorization token not provided'})
            #     return self.send_response(request, response)
            
            # if isinstance(user, str):
            #     user = json.loads(user)

            # if "admin" not in user.get("roles", []):
            #     response = Response.unauthorized({'message': 'Authorization token not provided'})
            #     return self.send_response(request, response)
            
            role_instance = role_collection.find_one_and_delete({"_id": ObjectId(pk)})
            if not role_instance:
                response = Response.not_found(format_response_data(404, "Not Found", None))
                return self.send_response(request, response)
            threading.Thread(target=thread_update_roles_users, args=(role_instance['name'],)).start()

            response = Response.ok(format_response_data(200, "Xóa role thành công", None))
        except Exception as e:
            print(e)
            response = Response.bad_request({"error": str(e)})
        self.send_response(request, response)