import pymongo
from pymongo import UpdateOne
from any import (
    POINT_KEY,
    IDENT_KEY
)


def as_is(timestamp, doc):
    return dict(timestamp=timestamp, **doc)


def pointing(timestamp, doc, lon_field=None, lat_field=None):
    if not lon_field:
        lon_field = 'lon'
    if not lat_field:
        lat_field = 'lat'
    return {**doc,
            'timestamp': timestamp,
            POINT_KEY: dict(type="Point", coordinates=[doc.get(lon_field), doc.get(lat_field), ])}


def mongodb_upsert(
        mongodb_connection_string,
        mongodb_db_name,
        mongodb_collection_name,
        uq_field,
        converter,
        **kwargs):
    def the_real_decorator(decorate_me):
        def wrapper(*args, **kwargs):
            timestamp, documents = decorate_me(*args, **kwargs)  # Сама функция
            print(timestamp, documents)
            with pymongo.MongoClient(mongodb_connection_string) as client:
                collection = client[mongodb_db_name][mongodb_collection_name]
                instructions = [
                    # UpdateOne({config.PK: doc[config.PK]}, {'$set': dict(timestamp=timestamp, **doc)}, upsert=True)
                    UpdateOne(
                        {
                            IDENT_KEY: doc[uq_field],
                            'timestamp': {'$lte': timestamp}
                        },
                        {
                            '$set': converter(timestamp, doc, **kwargs.get('converter', dict()))
                        },
                        upsert=True
                    )
                    for doc in documents
                ]
                if instructions:
                    collection.bulk_write(instructions)

        return wrapper

    return the_real_decorator
