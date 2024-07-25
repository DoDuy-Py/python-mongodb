from views.users import UserViewSet
from views.roles import RoleViewSet
from views.weather import WeatherViewSet
from views.water import WaterViewSet

from auth.auth import Auth
from auth.auth import Token

routes = {
    "GET": {
        "/users": UserViewSet().get,
        "/profile/{pk}": UserViewSet().detail,

        "/roles": RoleViewSet().get,

        "/weathers": WeatherViewSet().get,
        "/weather/{pk}": WeatherViewSet().detail,

        "/waters": WaterViewSet().get,
        "/water/{pk}": WaterViewSet.detail
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