import schedule
from bson import ObjectId
from core.settings import water_collection, weather_collection
import time
import random
from datetime import datetime

from pymongo import InsertOne

import logging
import os

# Đảm bảo rằng thư mục tồn tại trước khi ghi logs
# log_directory = '/var/log/backend'
# if not os.path.exists(log_directory):
#     os.makedirs(log_directory)

logging.basicConfig(
    # filename=os.path.join(log_directory, 'logs-backend.log'),
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s  ',
    datefmt='%d-%m-%y %H:%M:%S',
    # level=logging.INFO
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def auto_increase(pk=None):
    try:
        logger.info(f"Run FUNCTION NAME: {auto_increase.__name__}")

        if pk:
            water_collection.update_one(
                {"_id": ObjectId(pk)},
                { "$inc": { "turbidity": 1 } }
            )

    except Exception as e:
        logger.error(e)

def auto_add():
    try:
        logger.info(f"Run FUNCTION NAME: {auto_add.__name__}")
        # Lấy tất cả thanh phố
        # hard code 
        locations = ("New York", "Wasington", "Cali", "Wasington DC", "Hà Nội")
        data = [
            {
                "location": location,
                "temperature": random.randint(0, 45),
                "humidity": random.randint(0, 15),
                "wind_speed": random.randint(0, 15),
                "visibility": random.randint(0, 15),
                "pressure": random.randint(0, 15),
                "precipitation": random.randint(0, 15),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            } for location in locations
        ]
        # weather_collection.bulk_write(data)
        result = weather_collection.insert_many(data)
        logger.info(f"================= Inserted IDs: {result.inserted_ids} ==============")

    except Exception as e:
        logger.error(e)

def auto_schedule_seconds():
    auto_increase("66a1eeab95fe3dc371f0ba5d")
def auto_schedule_minutes():
    auto_add()


def init_schedule():
    try:
        logger.info(f"======= Run Schedule ========")
        # return
        # schedule.every(1).seconds.do(auto_schedule_seconds)
        schedule.every(5).seconds.do(auto_schedule_minutes)
        while True:
            # logger.info(f"Running pending tasks...")
            schedule.run_pending()
            time.sleep(0.5)
    except Exception as e:
        print(e)
        logger.error(f"ERORR ============ {e}")