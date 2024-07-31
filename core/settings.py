from pymongo import MongoClient
import redis
import os

import logging

# log_directory = '/var/log/backend'
# if not os.path.exists(log_directory):
#     os.makedirs(log_directory)

logging.basicConfig(
    # filename=os.path.join(log_directory, 'logs-backend.log'),
    format='%(asctime)s %(levelname)s %(message)s',
    filemode='w'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

mongodb_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
logger.info(os.getenv('MONGODB_URL'))

client = MongoClient(mongodb_url)
database = client.my_database

user_collection = database.get_collection("users")
role_collection = database.get_collection("roles")
water_collection = database.get_collection("waters")
weather_collection = database.get_collection("weathers")

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