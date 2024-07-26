import json
from urllib.parse import parse_qs, urlparse
from bson import ObjectId
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from auth.auth_token import validate_token
from core.settings import water_collection
from core.base import Base, Response
from views_func.decorator import permission_required
from views_func.function import format_response_data


class WaterViewSet(Base):
    '''
        @API CRUD for Water
    '''

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

            required_fields = {
                "name": None,
                "location": None,
                "ph_level": None,
                "temperature": None,
                "turbidity": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
                # "created_by": None
                # "updated_by": None
            }
            
            water_data = json.loads(post_data)
            ## validate data post
            new_water = {key: water_data.get(key, default_value) for key, default_value in required_fields.items()}
            # water_data["created_at"] = datetime.utcnow()
            # water_data["updated_at"] = datetime.utcnow()
            # water_data["updated_by"] = str(user['_id'])
            # water_data["created_by"] = str(user['_id'])

            result = water_collection.insert_one(new_water)

            new_water["_id"] = str(result.inserted_id)

            response = Response.ok(format_response_data(200, "Thêm dữ liệu thành công", new_water))
            return self.send_response(request, response)
        except Exception as e:
            print(e)
            response = Response.bad_request(format_response_data(400, "Có lỗi xảy ra", None))
            return self.send_response(request, response)
    
    @permission_required(permissions=['staff'])
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
            
            # Lấy các query parameters từ URL
            query_params = parse_qs(urlparse(request.path).query)

            # keyword = query_params.get('keyword', '')
            # page = int(query_params.get('page', 1))  # Trang hiện tại (mặc định là 1)
            # per_page = int(query_params.get('per_page', 10))  # Số lượng bản ghi trên mỗi trang (mặc định là 10)

            keyword = ''
            if 'keyword' in query_params and query_params['keyword']:
                keyword = query_params['keyword'][0]
            page = 1
            if 'page' in query_params and query_params['page']:
                page = int(query_params['page'][0])
            per_page = 10
            if 'per_page' in query_params and query_params['per_page']:
                per_page = int(query_params['per_page'][0])
            
            waters = list(water_collection.find(
                { "name": { "$regex": keyword, '$options': 'i' } }
            ).skip(page).limit(per_page).sort("created_at", -1))

            for water in waters:
                water["_id"] = str(water["_id"])

            # Tính tổng số bản ghi thỏa mãn điều kiện
            total_count = len(waters)
            total_pages = (total_count + per_page - 1) // per_page  # Tính tổng số trang

            # Tạo phản hồi
            response_data = {
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'total_count': total_count,
                'content': waters
            }

            response = Response.ok(format_response_data(200, "Lấy danh sách user thành công", response_data))
            return self.send_response(request, response)
        except Exception as e:
            print(e)
            response = Response.bad_request(format_response_data(400, "Có lỗi xảy ra", None))
            return self.send_response(request, response)
    
    @permission_required(permissions=['staff'])
    def detail(self, request, pk=None):
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
            
            water = water_collection.find_one({"_id": ObjectId(pk)})
            if not water:
                response = Response.not_found(format_response_data(404, "Not Found", None))
                return self.send_response(request, response)

            water["_id"] = str(water["_id"])
            response = Response.ok(format_response_data(200, "Lấy thông tin user thành công", water))
            return self.send_response(request, response)
        except Exception as e:
            response = Response.bad_request(format_response_data(400, "Có lỗi xảy ra", None))
            return self.send_response(request, response)
    
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

            # if "admin" not in user.get("roles", []):
            #     response = Response.unauthorized({'message': 'Authorization token not provided'})
            #     return self.send_response(request, response)
            
            content_length = int(request.headers['Content-Length'])
            post_data = request.rfile.read(content_length)

            required_fields = {
                "name": None,
                "location": None,
                "ph_level": None,
                "temperature": None,
                "turbidity": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
                # "created_by": None
                # "updated_by": None
            }

            input_data = json.loads(post_data)
            new_data = {key: value for key, value in input_data if key in required_fields.keys()}
            result = water_collection.update_one(
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

            # if "admin" not in user.get("roles", []):
            #     response = Response.unauthorized({'message': 'Authorization token not provided'})
            #     return self.send_response(request, response)
            
            water = water_collection.find_one_and_delete({"_id": ObjectId(pk)})
            if not water:
                response = Response.not_found(format_response_data(404, "Not Found", None))
                return self.send_response(request, response)
            
            response = Response.ok(format_response_data(200, "Xóa user thành công", None))
        except Exception as e:
            response = Response.bad_request({"error": str(e)})
        self.send_response(request, response)