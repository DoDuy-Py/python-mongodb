import json
import os
import uuid

from bson import ObjectId
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from auth.auth_token import validate_token
from core.settings import weather_collection, static, media
from core.base import Base, Response
from views_func.decorator import permission_required
from views_func.function import format_response_data

from urllib.parse import parse_qs, urlparse
from dateutil import parser
import cgi

import urllib.request
# url = 'http://example.com/image.jpg' # The image URL
# urllib.request.urlretrieve(url, 'new_image.jpg') # Save the image


class WeatherViewSet(Base):
    '''
        @API CRUD for Weather
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
            
            weather_data = json.loads(post_data)
            weather_data["created_at"] = datetime.utcnow()
            weather_data["updated_at"] = datetime.utcnow()
            # weather_data["updated_by"] = str(user['_id'])
            # weather_data["created_by"] = str(user['_id'])

            result = weather_collection.insert_one(weather_data)

            weather_data["_id"] = str(result.inserted_id)

            response = Response.ok(format_response_data(200, "Thêm dữ liệu thành công", weather_data))
            return self.send_response(request, response)
        except Exception as e:
            print(e)
            response = Response.bad_request(format_response_data(400, "Có lỗi xảy ra", None))
            return self.send_response(request, response)
    
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

            query = {}
            if keyword:
                query["name"] = { "$regex": keyword, '$options': 'i' }
                        
            weathers = list(weather_collection.find(query).skip(page).limit(per_page).sort("created_at", -1))

            for weather in weathers:
                weather["_id"] = str(weather["_id"])

            # Tính tổng số bản ghi thỏa mãn điều kiện
            total_count = len(weathers)
            total_pages = (total_count + per_page - 1) // per_page  # Tính tổng số trang

            # Tạo phản hồi
            response_data = {
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'total_count': total_count,
                'content': weathers
            }

            response = Response.ok(format_response_data(200, "Lấy danh sách user thành công", response_data))
            return self.send_response(request, response)
        except Exception as e:
            print(e)
            response = Response.bad_request(format_response_data(400, "Có lỗi xảy ra", None))
            return self.send_response(request, response)
    
    @permission_required(permissions=['staff', 'admin'])
    def get_temperature_avg_in_citys(self, request):
        try:
            # Lấy các query parameters từ URL
            query_params = parse_qs(urlparse(request.path).query)

            keyword = ''
            if 'keyword' in query_params and query_params['keyword']:
                keyword = query_params['keyword'][0]
            cities = []
            if 'cities' in query_params and query_params['cities']:
                cities = query_params['cities'][0]
                cities = cities.split(",")

            start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
            if 'start_time' in query_params and query_params['start_time']:
                start_time = parser.parse(query_params['start_time'][0])
            if 'end_time' in query_params and query_params['end_time']:
                end_time = parser.parse(query_params['end_time'][0])

            page = 1
            if 'page' in query_params and query_params['page']:
                page = int(query_params['page'][0])
            per_page = 100
            if 'per_page' in query_params and query_params['per_page']:
                per_page = int(query_params['per_page'][0])
            
            # Tạo điều kiện truy vấn
            query = {
                # "city": {"$in": cities},
                # "name": { "$regex": keyword, '$options': 'i' },
                "created_at": {"$gte": start_time, "$lte": end_time}
            }
            if keyword:
                query["name"] = { "$regex": keyword, '$options': 'i' }
            # Nếu có danh sách thành phố thì thêm điều kiện lọc theo city
            if cities:
                query["city"] = {"$in": cities}

            # Sử dụng pipeline của aggregation để tính giá trị trung bình của nhiệt độ
            pipeline = [
                {"$match": query},
                {"$addFields": {
                    "temperature_as_float": {"$toDouble": "$temperature"}  # Chuyển đổi từ str sang float
                }},
                {"$group": {
                    "_id": None,
                    "averageTemperature": {"$avg": "$temperature_as_float"}
                }}
            ]

            result = list(weather_collection.aggregate(pipeline))

            # for weather in weathers:
            #     weather["_id"] = str(weather["_id"])

            # Tính tổng số bản ghi thỏa mãn điều kiện
            total_count = len(result)
            total_pages = (total_count + per_page - 1) // per_page  # Tính tổng số trang

            # Tạo phản hồi
            response_data = {
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'total_count': total_count,
                'content': result
            }

            response = Response.ok(format_response_data(200, "Lấy danh sách user thành công", response_data))
            return self.send_response(request, response)
        except Exception as e:
            print(e)
            response = Response.bad_request(format_response_data(400, "Có lỗi xảy ra", None))
            return self.send_response(request, response)
    
    @permission_required(permissions=['staff', 'admin'])
    def get_avg_temperature_of_city(self, request):
        try:
            # Lấy các query parameters từ URL
            query_params = parse_qs(urlparse(request.path).query)

            keyword = ''
            if 'keyword' in query_params and query_params['keyword']:
                keyword = query_params['keyword'][0]
            cities = []
            if 'cities' in query_params and query_params['cities']:
                cities = query_params['cities'][0]
                cities = cities.split(",")

            start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
            if 'start_time' in query_params and query_params['start_time']:
                start_time = parser.parse(query_params['start_time'][0])
            if 'end_time' in query_params and query_params['end_time']:
                end_time = parser.parse(query_params['end_time'][0])

            page = 1
            if 'page' in query_params and query_params['page']:
                page = int(query_params['page'][0])
            per_page = 10
            if 'per_page' in query_params and query_params['per_page']:
                per_page = int(query_params['per_page'][0])
            
            # Tạo điều kiện truy vấn
            query = {
                # "city": {"$in": cities},
                # "name": { "$regex": keyword, '$options': 'i' },
                "created_at": {"$gte": start_time, "$lte": end_time}
            }
            if keyword:
                query["name"] = { "$regex": keyword, '$options': 'i' }
            # Nếu có danh sách thành phố thì thêm điều kiện lọc theo city
            if cities:
                query["city"] = {"$in": cities}

            # Sử dụng pipeline của aggregation để tính giá trị trung bình của nhiệt độ
            pipeline = [
                {"$match": query},
                {"$addFields": {
                    "temperature_as_float": {"$toDouble": "$temperature"}  # Chuyển đổi từ str sang float
                }},
                {"$group": {
                    "_id": "$name",
                    "averageTemperature": {"$avg": "$temperature_as_float"}
                }}
            ]

            result = list(weather_collection.aggregate(pipeline))

            # for weather in weathers:
            #     weather["_id"] = str(weather["_id"])

            # Tính tổng số bản ghi thỏa mãn điều kiện
            total_count = len(result)
            total_pages = (total_count + per_page - 1) // per_page  # Tính tổng số trang

            # Tạo phản hồi
            response_data = {
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'total_count': total_count,
                'content': result
            }

            response = Response.ok(format_response_data(200, "Lấy danh sách user thành công", response_data))
            return self.send_response(request, response)
        except Exception as e:
            print(e)
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
            
            weather = weather_collection.find_one({"_id": ObjectId(pk)})
            if not weather:
                response = Response.not_found(format_response_data(404, "Not Found", None))
                return self.send_response(request, response)

            weather["_id"] = str(weather["_id"])
            response = Response.ok(format_response_data(200, "Lấy thông tin user thành công", weather))
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

            # if "admin" not in user.get("roles", []):
            #     response = Response.unauthorized({'message': 'Authorization token not provided'})
            #     return self.send_response(request, response)
            
            content_length = int(request.headers['Content-Length'])
            post_data = request.rfile.read(content_length)

            new_data = json.loads(post_data)
            result = weather_collection.update_one(
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
            
            weather = weather_collection.find_one_and_delete({"_id": ObjectId(pk)})
            if not weather:
                response = Response.not_found(format_response_data(404, "Not Found", None))
                return self.send_response(request, response)
            
            response = Response.ok(format_response_data(200, "Xóa user thành công", None))
        except Exception as e:
            response = Response.bad_request({"error": str(e)})
        self.send_response(request, response)
    

    ## POST WITH FILE
    @permission_required(permissions=['admin'])
    def create_with_file(self, request):
        try:
            content_type, pdict = cgi.parse_header(request.headers['Content-Type'])
            if content_type != 'multipart/form-data':
                response = Response.bad_request({'message': 'Content-Type must be multipart/form-data'})
                return self.send_response(request, response)

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
            
            form = cgi.FieldStorage(
                fp=request.rfile, headers=request.headers, 
                environ={'REQUEST_METHOD': 'POST'}
            )

            weather_data = {}
            for key in form.keys():
                if key != 'file':
                    weather_data[key] = form.getvalue(key)
            weather_data["created_at"] = datetime.utcnow()
            weather_data["updated_at"] = datetime.utcnow()
            # weather_data["updated_by"] = str(user['_id'])
            # weather_data["created_by"] = str(user['_id'])

            # Xử lý file tải lên
            if 'file' in form:
                file = form['file']
                if file.file:
                    # file_path = os.path.join(static, file.filename)
                    if not os.path.exists("static/weather"):
                        os.makedirs("static/weather")
                    new_file_name = f'weather-{str(uuid.uuid4().hex)}-{datetime.now().strftime("%Y-%m-%d-%H:%M").replace(":", "-")}.png'
                    file_path = os.path.join(f"{static}/weather", new_file_name)
                    file_content = file.file.read()
                    with open(file_path, 'wb') as output_file:
                        output_file.write(file_content)
                    weather_data['file_path'] = file_path
            
            result = weather_collection.insert_one(weather_data)
            weather_data["_id"] = str(result.inserted_id)
            
            response = Response.ok(format_response_data(200, "Thêm dữ liệu thành công", weather_data))
            return self.send_response(request, response)
        except Exception as e:
            print(e)
            response = Response.bad_request(format_response_data(400, "Có lỗi xảy ra", None))
            return self.send_response(request, response)
