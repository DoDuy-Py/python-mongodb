from core.base import json_serialize, Base, Response
from core.settings import user_collection
from views_func.function import format_response_data
from .auth_token import refresh_access_token, verify_password, hash_password, create_access_token

import json
from datetime import datetime


class Auth(Base):

    def signin(self, request):
        content_length = int(request.headers['Content-Length'])
        post_data = request.rfile.read(content_length)
        try:
            user_data = json.loads(post_data)
            account = user_data.get('account')
            password = user_data.get('password')
            if not account or not password:
                response = {
                    "statusCode": 404,
                    "body": {"message": "Vui lòng nhập đầy đủ thông tin tài khoản"},
                    "headers": {"Content-Type": "application/json"}
                }
                return self.send_response(request, response)
            
            user = user_collection.find_one({"account": account})
            # print(type(user))
            if not user:
                response = Response.not_found({"message": "Tài khoản không tồn tại"})
                return self.send_response(request, response)
            
            if not verify_password(password, user['password']):
                response = Response.not_found({"message": "Mật khẩu không chính xác"})
                return self.send_response(request, response)
            
            access_token = create_access_token(user)
            response = Response.ok(access_token)

            # if user:
            #     response = Response.ok({"message": "Đăng nhập thành công"})
            # else:
            #     response = Response.not_found({"message": "Tài khoản hoặc mật khẩu không đúng"})
            return self.send_response(request, response)

        except Exception as e:
            response = Response.bad_request({"error": str(e)})
            return self.send_response(request, response)

    def signup(self, request):
        content_length = int(request.headers['Content-Length'])
        post_data = request.rfile.read(content_length)
        try:
            user_data = json.loads(post_data)
            account = user_data.get('account')
            password = user_data.get('password')
            if not account or not password:
                response = {
                    "statusCode": 404,
                    "body": {"message": "Vui lòng nhập đầy đủ thông tin tài khoản"},
                    "headers": {"Content-Type": "application/json"}
                }
                return self.send_response(request, response)
            
            user = user_collection.find_one({"account": account})
            if user:
                response = Response.not_found({"message": "Tài khoản đã tồn tại"})
                return self.send_response(request, response)
            
            hashed_password = hash_password(password)
            
            user_data["created_at"] = datetime.utcnow()
            user_data["password"] = hashed_password
            result = user_collection.insert_one(user_data)
            user_data["_id"] = str(result.inserted_id)
            response = Response.ok({"message": "Đăng ký thành công"})

            return self.send_response(request, response)

        except Exception as e:
            response = Response.bad_request({"error": str(e)})
            return self.send_response(request, response)
    

class Token(Base):
    # API Endpoint for Refresh Token
    def _handle_refresh_token(self, request):
        try:
            content_length = int(request.headers['Content-Length'])
            post_data = request.rfile.read(content_length)
            data = json.loads(post_data)
            refresh_token = data.get("refresh_token")
            
            if not refresh_token:
                response = Response.UNAUTHORIZED({'message': "Refresh token not provided"})
                return self.send_response(request, response)

            new_tokens = refresh_access_token(refresh_token)
            response = Response.ok(format_response_data(200, "Token refreshed successfully", new_tokens))
        except Exception as e:
            response = Response.bad_request({"error": str(e)})
        
        self.send_response(request, response)