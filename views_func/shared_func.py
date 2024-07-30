import schedule
from bson import ObjectId
from core.settings import water_collection, weather_collection
import time
import random
from datetime import datetime

from pymongo import InsertOne

def auto_increase(pk=None):
    try:
        print(f"Run FUNCTION NAME: {auto_increase.__name__}")

        if not pk:
            water_collection.update_one(
                {"_id": ObjectId(pk)},
                { "$inc": { "turbidity": 1 } }
            )

    except Exception as e:
        print(e)

def auto_add():
    try:
        print(f"Run FUNCTION NAME: {auto_add.__name__}")
        # Lấy tất cả thanh phố
        # hard code 
        locations = ("New York", "Wasington", "Cali", "Wasington DC", "Hà Nội")
        data = [
            InsertOne({
                "location": location,
                "temperature": random.randint(0, 45),
                "humidity": random.randint(0, 15),
                "wind_speed": random.randint(0, 15),
                "visibility": random.randint(0, 15),
                "pressure": random.randint(0, 15),
                "precipitation": random.randint(0, 15),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }) for location in locations
        ]
        weather_collection.bulk_write(data)

    except Exception as e:
        print(e)

def auto_schedule_seconds():
    auto_increase("66a1eeab95fe3dc371f0ba5d")
def auto_schedule_minutes():
    auto_add()


def init_schedule():
    print(f"======= Run Schedule ========")
    # return
    # schedule.every(1).seconds.do(auto_schedule_seconds)
    schedule.every(10).minutes.do(auto_schedule_minutes)
    while True:
        schedule.run_pending()
        time.sleep(0.5)