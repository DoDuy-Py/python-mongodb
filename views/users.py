import json
from bson import ObjectId, json_util
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from auth.auth_token import validate_token
from core.settings import user_collection
from core.base import json_serialize, Base, Response
from views_func.decorator import permission_required
from views_func.function import format_response_data

class UserViewSet(Base):

    @permission_required(permissions=['admin'])
    def create(self, request):
        content_length = int(request.headers['Content-Length'])
        post_data = request.rfile.read(content_length).decode('utf-8')
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
            # if "admin" not in user.get('roles', []):
            #     response = Response.unauthorized({'message': 'Authorization token not provided'})
            #     return self.send_response(request, response)
            
            user_data = json.loads(post_data)
            user_data["created_at"] = datetime.utcnow()
            result = user_collection.insert_one(user_data)
            user_data["_id"] = str(result.inserted_id)
            response = Response.ok(user_data)
        except Exception as e:
            response = Response.bad_request({"error": str(e)})
        self.send_response(request, response)

    def get(self, request):
        try:
            auth = request.headers.get("Authorization")
            if not auth:
                response = Response.unauthorized({'message': 'Authorization token not provided'})
                return self.send_response(request, response)
            
            user = validate_token(auth)
            if not user:
                response = Response.unauthorized({'message': 'Authorization token not provided'})
                return self.send_response(request, response)
            # print(type(user))
            # if isinstance(user, str):
            #     user = json.loads(user)
            # if "admin" not in user.get('roles', []):
            #     response = Response.unauthorized({'message': 'Authorization token not provided'})
            #     return self.send_response(request, response)
            
            users = list(user_collection.find())
            for user in users:
                user["_id"] = str(user["_id"])
            response = Response.ok(format_response_data(200, "Lấy danh sách user thành công", users))
            return self.send_response(request, response)
        except Exception as e:
            response = Response.bad_request(format_response_data(400, "Có lỗi xảy ra", None))
            return self.send_response(request, response)
    
    def detail(self, request, pk=None):
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

            if "admin" not in user.get("roles", []) and str(pk) != user.get("_id"):
                response = Response.unauthorized({'message': 'Authorization token not provided'})
                return self.send_response(request, response)
            
            user = user_collection.find_one({"_id": ObjectId(pk)})
            if not user:
                response = Response.not_found(format_response_data(404, "Not Found", None))
                return self.send_response(request, response)

            user["_id"] = str(user["_id"])
            response = Response.ok(format_response_data(200, "Lấy thông tin user thành công", user))
        except Exception as e:
            response = Response.bad_request({"error": str(e)})
        self.send_response(request, response)

    @permission_required(permissions=['admin'])
    def update(self, request, pk=None):
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

            # if "admin" not in user.get("roles", []) and str(pk) != user.get("_id"):
            #     response = Response.unauthorized({'message': 'Authorization token not provided'})
            #     return self.send_response(request, response)
            
            # user = user_collection.find_one({"_id": ObjectId(pk)})
            # if not user:
            #     response = Response.not_found(format_response_data(404, "Not Found", None))
            #     return self.send_response(request, response)
            
            content_length = int(request.headers['Content-Length'])
            post_data = request.rfile.read(content_length).decode('utf-8')

            new_data = json.loads(post_data)
            result = user_collection.update_one(
                {"_id": ObjectId(pk)},
                {"$set": new_data}
            )
            if result.matched_count == 0:
                response = Response.not_found(format_response_data(404, "Not Found", None))
                return self.send_response(request, response)
            
            response = Response.ok(format_response_data(200, "Update user thành công", None))
        except Exception as e:
            print(e)
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

            # if "admin" not in user.get("roles", []) and str(pk) != user.get("_id"):
            #     response = Response.unauthorized({'message': 'Authorization token not provided'})
            #     return self.send_response(request, response)
            
            user = user_collection.find_one({"_id": ObjectId(pk)})
            if not user:
                response = Response.not_found(format_response_data(404, "Not Found", None))
                return self.send_response(request, response)
            
            user_collection.delete_one({"_id": ObjectId(pk)})
            response = Response.ok(format_response_data(200, "Xóa user thành công", None))
        except Exception as e:
            response = Response.bad_request({"error": str(e)})
        self.send_response(request, response)