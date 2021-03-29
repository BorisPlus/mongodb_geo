import datetime
import requests
from common import base_config


# curl -d '{"simplify":true,"classes":["econom"],"id":"000000000000000000000000000000",
# "point":[30.33606681550002,59.936871546400001],
# "supported":["code_dispatch"],"full_adjust_task":true,"current_drivers":[]}'
# -XPOST  'https://tc.mobile.yandex.net/3.0/nearestdrivers?block_id=default'
# -H 'Content-Type: application/json; charset=utf-8'

def get_data(lon_lat):
    _lon, _lat = lon_lat
    timestamp = datetime.datetime.now().timestamp()
    response = requests.post(
        'https://tc.mobile.yandex.net/3.0/nearestdrivers?block_id=default',
        json={"simplify": True,
              "classes": ["econom"],
              "id": "5c53ba9e9c522b48f79ba9dac9ac38ac",
              "point": [_lon, _lat, ],
              # "supported": ["code_dispatch"],
              # "full_adjust_task": True,
              "current_drivers": []
              }
    )
    if response.ok:
        dict_data = response.json()
        if 'drivers' in dict_data:
            dict_data = dict_data.get('drivers')
        return timestamp, dict_data
    return timestamp, []


if __name__ == '__main__':
    print(get_data((base_config.LON, base_config.LAT,)))
