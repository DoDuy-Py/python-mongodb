from pymongo import MongoClient

MONGO_DETAILS = "mongodb://localhost:27017"

client = MongoClient(MONGO_DETAILS)
database = client.my_database

user_collection = database.get_collection("users")
role_collection = database.get_collection("roles")
water_collection = database.get_collection("waters")
weather_collection = database.get_collection("Weathers")

# JWT
ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24 * 7 # 7 days
SECRET_KEY = 'secret'
SECURITY_ALGORITHM = 'HS256'

static = 'static'
media = 'media'