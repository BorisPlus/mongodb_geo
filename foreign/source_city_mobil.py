import datetime
import requests
from common import base_config


def get_data(lon_lat):
    _lon, _lat, = lon_lat
    timestamp = datetime.datetime.now().timestamp()
    response = requests.post(
        'https://c-api.city-mobil.ru/getdrivers',
        json={"latitude": _lat,
              # "limit": 10,
              "limit": None,
              "longitude": _lon, "method": "getdrivers",
              "radius": 1,
              "tariff_group": [1, 2, 3, 4, 5, 6], "ver": None}
    )
    # "tariff_group": [1, 2, 3, 4, 5, 6], "ver": "4.33.0"}
    if response.ok:
        dict_data = response.json()
        if 'drivers' in dict_data:
            dict_data = dict_data.get('drivers')
        return timestamp, dict_data
    return timestamp, []


if __name__ == '__main__':
    import pprint

    pprint.pprint(get_data((base_config.LON, base_config.LAT,)))
