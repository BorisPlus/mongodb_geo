import pymongo
import datetime
from upsert_city_mobil import MONGODB_DB_COLLECTION_NAME
from common import base_config


def for_delete(timestamp_older):
    with pymongo.MongoClient(base_config.MONGODB_CONNECTION_STRING) as client:
        return client[base_config.MONGODB_DB_NAME][MONGODB_DB_COLLECTION_NAME].delete_many(
            {"timestamp": {"$lt": timestamp_older}})


def for_delete_all():
    with pymongo.MongoClient(base_config.MONGODB_CONNECTION_STRING) as client:
        return client[base_config.MONGODB_DB_NAME][MONGODB_DB_COLLECTION_NAME].delete_many({})


if __name__ == '__main__':
    print(for_delete(datetime.datetime.now().timestamp()).deleted_count)
    print(for_delete_all().deleted_count)
