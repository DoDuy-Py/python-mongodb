from datetime import datetime
from bson import ObjectId
from typing import List, Optional
from pymongo import MongoClient

class User:
    username: str
    password: str
    roles: list = []


class Water:
    name: str
    location: str
    ph_level: str
    temperature: str
    turbidity: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    created_by: str
    updated_by: str


class Weather:
    name: str
    temperature: float 
    humidity: float
    wind_speed: float
    visibility: float
    pressure: float
    precipitation: float
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    created_by: str
    updated_by: str


class Role:
    name: str
    permissions: List[str]
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    created_by: str
    updated_by: str