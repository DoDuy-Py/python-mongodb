from pymongo import MongoClient
import redis
import os

mongodb_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')

client = MongoClient(mongodb_url)
database = client.my_database

user_collection = database.get_collection("users")
role_collection = database.get_collection("roles")
water_collection = database.get_collection("waters")
weather_collection = database.get_collection("Weathers")

# JWT
ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24 * 7 # 7 days
SECRET_KEY = 'secret'
SECURITY_ALGORITHM = 'HS256'

# Cấu hình Redis
r = redis.StrictRedis(host='redis', port=6379, db=0)

RATE_LIMIT = 10  # Số lượng request tối đa mỗi ngày
TIME_CACHED_RATE_LIMIT = 86400  # 1 ngày (tính bằng giây)

static = 'static'
media = 'media'