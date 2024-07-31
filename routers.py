from views.users import UserViewSet
from views.roles import RoleViewSet
from views.weather import WeatherViewSet
from views.water import WaterViewSet

from auth.auth import Auth
from auth.auth import Token
import re
from datetime import datetime

from core.settings import r, RATE_LIMIT, TIME_CACHED_RATE_LIMIT
from views_func.shared_func import logger

routes = {
    "GET": {
        "/users": UserViewSet().get,
        "/profile/{pk}": UserViewSet().detail,

        "/roles": RoleViewSet().get,

        "/weathers": WeatherViewSet().get,
        "/get-temperature-avg-in-citys": WeatherViewSet().get_temperature_avg_in_citys,
        "/get-avg-temperature-of-city": WeatherViewSet().get_avg_temperature_of_city,
        "/weather/{pk}": WeatherViewSet().detail,

        "/waters": WaterViewSet().get,
        "/water/{pk}": WaterViewSet().detail
    },
    "POST": {
        "/sign-in": Auth().signin,
        "/sign-up": Auth().signup,

        "/create-user": UserViewSet().create,

        "/create-role": RoleViewSet().create,

        "/create-weather": WeatherViewSet().create,
        "/create-weather-file": WeatherViewSet().create_with_file,

        "/create-water": WaterViewSet().create,

        # refresh token
        "/refresh-token": Token()._handle_refresh_token
    },
    "PUT": {
        "/edit-user/{pk}": UserViewSet().update
    },
    "DELETE": {
        "/delete-user/{pk}": UserViewSet().delete,

        "/delete-role/{pk}": RoleViewSet().delete,

        "/delete-weather/{pk}": WeatherViewSet().delete,

        "/delete-water/{pk}": WaterViewSet().delete
    }
}

RATE_LIMITS = {
    "GET": {
        "/users": 10,
        "/profile/{pk}": 10,
        "/roles": 10,
        "/weathers": 10,
        "/get-temperature-avg-in-citys": 10,
        "/get-avg-temperature-of-city": 10,
        "/weather/{pk}": 10,
        "/waters": 10,
        "/water/{pk}": 10
    },
    "POST": {
        "/sign-in": 10,
        "/sign-up": 10,
        "/create-user": 10,
        "/create-role": 10,
        "/create-weather": 10,
        "/create-weather-file": 10,
        "/create-water": 10,
        "/refresh-token": 10
    },
    "PUT": {
        "/edit-user/{pk}": 10
    },
    "DELETE": {
        "/delete-user/{pk}": 10,
        "/delete-role/{pk}": 10,
        "/delete-weather/{pk}": 10,
        "/delete-water/{pk}": 10
    }
}

def route_request(path, method):
    if "?" in path:
        path = path.split("?")[0]
    # # Static routes
    if method in routes and path in routes[method]:
        return routes[method][path], None
    # Handle dynamic routes
    for route in routes[method]:
        if "{" in route and "}" in route:
            base_route, param = route.split("/{")
            if path.startswith(base_route):
                return routes[method][route], path[len(base_route)+1:]
    # return routes.get(method, {}).get(path, None), None
    return None, None

# Limit call apis
def rate_limit(user_id, method, path):
    logger.info(f"================= {rate_limit.__name__} ==============")
    if "?" in path:
        path = path.split("?")[0]
    # Tìm route tương ứng với path động
    for route, limit in RATE_LIMITS.get(method, {}).items():
        if re.fullmatch(route.replace("{pk}", r"[\w-]+"), path):
            current_time = datetime.now()
            start_of_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            key = f"api_rate_limit:{user_id}:{method}:{route}"

            # Tính time cache đến 24h
            end_of_day = current_time.replace(hour=23, minute=59, second=59, microsecond=999999)
            expiration_time = int((end_of_day - current_time).total_seconds())
            
            # Tăng số lượng yêu cầu của người dùng
            requests = r.incr(key)
            # Nếu key mới được tạo, thiết lập thời gian hết hạn cho key
            if requests == 1:
                r.expire(key, expiration_time)

            if requests > limit:
                return False, limit - requests + 1
            else:
                return True, limit - requests + 1
    
    # Nếu không tìm thấy route tương ứng
    return True, None