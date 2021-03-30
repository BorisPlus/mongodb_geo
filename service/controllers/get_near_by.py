import json

import pymongo
from bson import json_util

from base_config import (
    MONGODB_CONNECTION_STRING,
    MONGODB_DB_NAME,
    POINT_OBJECT,
    POLYGON_OBJECT,
    DEFAULT_OBJECT_VIEW
)

PRINT_DEBUG = 0

MONGODB_DB_COLLECTIONS = dict(
    static={
        "geo_wikimapia_polygons": {
            "area": POLYGON_OBJECT,
        },
        "meteorites": {
            "location": POINT_OBJECT,
        },
    }
)


def print_debug(*args, **kwargs):
    if PRINT_DEBUG:
        print(*args, **kwargs)


def get_response(environ, start_response, app_config, lat, lon, distance):
    """
    Get geo data in geo circle.

    :param environ:
    :param start_response:
    :param app_config:
    :param lat:
    :param lon:
    :param distance:
    :return:
    """
    print_debug('\t', float(lat), float(lon), float(distance))
    start_response('200 OK', [('Content-Type', 'text/plain; charset=utf-8')])  # application/json
    dataset = []
    with pymongo.MongoClient(MONGODB_CONNECTION_STRING) as client:
        for geo_object_view in MONGODB_DB_COLLECTIONS:
            for collection_name in MONGODB_DB_COLLECTIONS.get(geo_object_view):
                collection = client[MONGODB_DB_NAME][collection_name]
                for geo_object_name in MONGODB_DB_COLLECTIONS.get(geo_object_view).get(collection_name):

                    print_debug('\t geo_object_view = ', geo_object_view)
                    print_debug('\t collection_name = ', collection_name)
                    print_debug('\t geo_object_name = ', geo_object_name)
                    geo_object_type = MONGODB_DB_COLLECTIONS. \
                        get(geo_object_view). \
                        get(collection_name). \
                        get(geo_object_name, DEFAULT_OBJECT_VIEW)
                    print_debug('\t geo_object_view = ', geo_object_view)
                    # TODO: было бы клево, но надо инверсить (X,Y) --> (Y,X) для Leaflet
                    data = dict(
                        collection_name=collection_name,
                        geo_object_name=geo_object_name,
                        geo_object_view=geo_object_view,
                        geo_object_type=geo_object_type,
                        data=list(collection.find({
                            # TODO:  planner returned error :: caused by ::
                            #  unable to find index for $geoNear query, full error:
                            #  {'ok': 0.0, 'errmsg': 'error processing query: ns=otus.meteoritesTree: GEONEAR
                            #  field=location maxdist=500 isNearSphere=0\nSort: {}\nProj: { _id: 0 }\n
                            #  planner returned error :: caused by :: unable to find index for
                            #  $geoNear query', 'code': 291, 'codeName': 'NoQueryExecutionPlans'}
                            geo_object_name: {
                                "$nearSphere": {
                                    "$geometry": {
                                        "type": "Point",
                                        "coordinates": [float(lon), float(lat)]
                                    },
                                    "$maxDistance": float(distance),
                                    "$minDistance": 0
                                }
                            }
                        }, {"_id": 0}))
                    )
                    dataset.append(data)
                    if PRINT_DEBUG:
                        for x in data.get('data'):
                            print_debug(x)
    return [bytes(json.dumps(dataset, ensure_ascii=False, default=json_util.default), 'utf-8')]
