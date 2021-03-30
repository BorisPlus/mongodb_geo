import pymongo
import json
from bson import json_util
from base_config import (
    MONGODB_CONNECTION_STRING,
    MONGODB_DB_NAME,
    MONGODB_DB_COLLECTIONS,
    DYNAMIC,
    STATIC,
    DEFAULT_OBJECT_TYPE
)

PRINT_DEBUG = 1


def print_debug(*args, **kwargs):
    if PRINT_DEBUG:
        print(*args, **kwargs)


def get_response(environ, start_response, app_config,
                 geo_object_view, north_east_lat, north_east_lon, south_west_lat, south_west_lon):
    """
    Get geo data in map polygon area.

    :param environ:
    :param start_response:
    :param app_config:
    :param geo_object_view: dynamic, static, all - geo object view
    :param north_east_lat:
    :param north_east_lon:
    :param south_west_lat:
    :param south_west_lon:
    :return:
    """
    print_debug('\t', geo_object_view)

    print_debug('\tnorth_east_lon', north_east_lon)
    north_east_lon = float(north_east_lon)
    if north_east_lon <= -180:
        north_east_lon = -180
    if north_east_lon >= 180:
        north_east_lon = 179.9999999
    print_debug('\t\tnorth_east_lon', north_east_lon)

    print_debug('\tnorth_east_lat', north_east_lat)
    north_east_lat = float(north_east_lat)
    if north_east_lat < -90:
        north_east_lat = -90
    if north_east_lat > 90:
        north_east_lat = 90
    print_debug('\t\tnorth_east_lat', north_east_lat)

    print_debug('\tsouth_west_lon', south_west_lon)
    south_west_lon = float(south_west_lon)
    if south_west_lon <= -180:
        south_west_lon = -180
    if south_west_lon >= 180:
        south_west_lon = 179.9999999
    print_debug('\t\tsouth_west_lon', south_west_lon)

    print_debug('\tsouth_west_lat', south_west_lat)
    south_west_lat = float(south_west_lat)
    if south_west_lat < -90:
        south_west_lat = -90
    if south_west_lat > 90:
        south_west_lat = 90
    print_debug('\t\tsouth_west_lat', south_west_lat)

    variants = tuple()
    if geo_object_view not in (DYNAMIC, STATIC, 'all'):
        geo_object_view = STATIC
    if geo_object_view == DYNAMIC:
        variants = (DYNAMIC,)
    if geo_object_view == STATIC:
        variants = (STATIC,)
    if geo_object_view == 'all':
        variants = (DYNAMIC, STATIC,)
    start_response('200 OK', [('Content-Type', 'text/plain; charset=utf-8')])  # application/json
    print_debug(variants)
    dataset = []
    with pymongo.MongoClient(MONGODB_CONNECTION_STRING) as client:
        for geo_object_view in filter(lambda x: x in variants, MONGODB_DB_COLLECTIONS):
            for collection_name in MONGODB_DB_COLLECTIONS.get(geo_object_view):
                collection = client[MONGODB_DB_NAME][collection_name]
                for geo_object_name in MONGODB_DB_COLLECTIONS.get(geo_object_view).get(collection_name):

                    print_debug('\t', geo_object_view)
                    print_debug('\t', collection_name)
                    print_debug('\t', geo_object_name)
                    print_debug('\t', MONGODB_DB_COLLECTIONS.
                                get(geo_object_view).
                                get(collection_name).
                                get(geo_object_name, DEFAULT_OBJECT_TYPE))
                    # TODO: было бы клево, но надо инверсить (X,Y) --> (Y,X) для Leaflet
                    # collection_geo_object = {}
                    data = dict(
                        collection_name=collection_name,
                        geo_object_name=geo_object_name,
                        geo_object_view=geo_object_view,
                        geo_object_type=MONGODB_DB_COLLECTIONS.
                            get(geo_object_view).
                            get(collection_name).
                            get(geo_object_name, DEFAULT_OBJECT_TYPE),
                        data=list(collection.find({
                            geo_object_name: {
                                "$geoIntersects": {
                                    "$geometry": {
                                        "type": "Polygon",
                                        "coordinates": [[
                                            # TODO: pymongo.errors.OperationFailure: Loop is not closed
                                            # [north_east_lon, north_east_lat],
                                            # [south_west_lon, north_east_lat],
                                            # [south_west_lon, south_west_lat],
                                            # [north_east_lon, south_west_lat],
                                            # [north_east_lon, north_east_lat]
                                            [north_east_lon, north_east_lat],
                                            [north_east_lon, south_west_lat],
                                            [south_west_lon, south_west_lat],
                                            [south_west_lon, north_east_lat],
                                            [north_east_lon, north_east_lat]
                                        ]]},
                                }
                            }
                        }, {"_id": 0}))
                    )
                    dataset.append(data)
                    print('len data', len(data.get('data')))
                    # if PRINT_DEBUG:
                    #     for x in data.get('data'):
                    #         print_debug(x)
    return [bytes(json.dumps(dataset, ensure_ascii=False, default=json_util.default), 'utf-8')]
