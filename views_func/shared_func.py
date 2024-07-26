import schedule
from bson import ObjectId
from core.settings import water_collection
import time

def auto_increase(pk=None):
    try:
        print(f"Run FUNCTION NAME: {auto_increase.__name__}")

        if pk:
            water_collection.update_one(
                {"_id": ObjectId(pk)},
                { "$inc": { "turbidity": 1 } }
            )

    except Exception as e:
        print(e)

def auto_schedule_seconds():
    auto_increase("66a1ee7595fe3dc371f0ba5b")


def init_schedule():
    print(f"======= Run Schedule ========")
    return
    schedule.every(1).seconds.do(auto_schedule_seconds)
    while True:
        schedule.run_pending()
        time.sleep(0.5)