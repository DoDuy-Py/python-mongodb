from datetime import datetime
from auth.auth_token import hash_password
from core.settings import user_collection, role_collection
from core.base import json_serialize
import json
from .shared_func import logger

def init_db():
    try:
        users = list(user_collection.find())
        if not users:
            logger.info("============= INIT USER ADMIN =============")
            user_data = {
                'account': 'admin',
                'password': hash_password('123'),
                'roles': ['admin'],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            user_collection.insert_one(user_data)

        roles = list(role_collection.find())
        if not roles:
            logger.info("============= INIT ROLE ADMIN, STAFF =============")
            roles_data = [
                {
                    "name": "admin",
                    "permission": ["view", "create", "update", "delete"],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                },
                {
                    "name": "staff",
                    "permission": ["view"],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            ]
            role_collection.insert_many(roles_data)

    except Exception as e:
        logger.error(e)

def format_response_data(status: int, message: str, data=None):
    data = {
        'code': status,
        'message': message,
        'data': data
    }
    # return json.dumps(data, default=json_serialize)
    return data

def thread_update_roles_users(role_name: str):
    try:
        # Cập nhật người dùng để loại bỏ vai trò đã bị xóa
        user_collection.update_many(
            {"roles": role_name},
            {"$pull": {"roles": role_name}}
        )
        logger.info(f"Role '{role_name}' đã bị xóa và tất cả các user có role này đã được cập nhật.")
    except Exception as e:
        logger.error(e)
    
    finally:
        pass