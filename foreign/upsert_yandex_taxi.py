from source_yandex_taxi import get_data as get_data_from_yandex_taxi
from upsert_any_formatting import mongodb_upsert
from datetime import datetime
from common import base_config

MONGODB_DB_COLLECTION_NAME = 'geo_yandex_taxi'
MONGODB_DB_COLLECTION_PK = 'id'

POINT_KEY = 'last_point'
LINESTRING_KEY = 'path'


def pointing_with_pathing(doc):
    if not doc.get("positions"):
        return {**doc}

    last_point = doc.get("positions")[0]
    line_coords = [
        [position.get('lon'), position.get('lat')] for position in doc.get("positions", [])
    ]
    if len(set([(x, y) for (x, y) in line_coords])) == 1:
        return {**doc,
                'timestamp': datetime.strptime(last_point.get("timestamp"), '%Y-%m-%dT%H:%M:%S.%f%z').timestamp(),
                POINT_KEY: dict(type="Point", coordinates=[last_point.get('lon'), last_point.get('lat')]),
                }
    return {**doc,
            'timestamp': datetime.strptime(last_point.get("timestamp"), '%Y-%m-%dT%H:%M:%S.%f%z').timestamp(),
            POINT_KEY: dict(type="Point", coordinates=[last_point.get('lon'), last_point.get('lat'), ]),
            LINESTRING_KEY: dict(type="LineString", coordinates=line_coords)
            }


# It is not work in pool
@mongodb_upsert(
    base_config.MONGODB_CONNECTION_STRING,
    base_config.MONGODB_DB_NAME,
    MONGODB_DB_COLLECTION_NAME,
    MONGODB_DB_COLLECTION_PK,
    pointing_with_pathing)
def upsert_yandex_taxi(*args, **kwargs):
    return get_data_from_yandex_taxi(*args, **kwargs)


if __name__ == '__main__':
    upsert_yandex_taxi((59.980312, 30.329998))

    # # AttributeError: Can't pickle local object...` when using multiprocessing
    # # https://github.com/pytorch/xla/issues/1554
