from service.user_def import load_jinja2_view_template as load_view
from base_config import (
    CONTAINS_DYNAMIC_DATA,
    LAT,
    LON,
)


def get_response(environ, start_response, app_config):
    return load_view(
        environ,
        start_response,
        app_config,
        'index.html',
        app_contains_dynamic=CONTAINS_DYNAMIC_DATA,
        # SPb
        map_lat_center=LAT,
        map_lon_center=LON,
    )
