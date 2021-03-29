try:
    from base_config import MONGODB_CONNECTION_STRING, MONGODB_DB_NAME
except ImportError:
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from base_config import MONGODB_CONNECTION_STRING, MONGODB_DB_NAME
from source_yandex_taxi import get_data as get_data_from_yandex_taxi
from upsert_yandex_taxi import (
    MONGODB_DB_COLLECTION_NAME,
    MONGODB_DB_COLLECTION_PK
)
import pymongo
# from pymongo import UpdateOne
# from pymongo.errors import BulkWriteError
import settings
from multiprocessing import Pool
from any import (
    IDENT_KEY,
)
from upsert_yandex_taxi import (
    pointing_with_pathing,
)


def local_print(*args, **kwargs):
    if __name__ == '__main__':
        print(*args, **kwargs, sep='\t')


def for_pooling(lon_lat):
    lon, lat = lon_lat
    timestamp, documents = get_data_from_yandex_taxi((lon, lat))

    local_print(lon, lat, timestamp, len(documents))

    with pymongo.MongoClient(MONGODB_CONNECTION_STRING) as client:
        collection = client[MONGODB_DB_NAME][MONGODB_DB_COLLECTION_NAME]
        # instructions = [
        #     UpdateOne(
        #         {
        #             IDENT_KEY: doc[MONGODB_DB_COLLECTION_PK],
        #             'timestamp': {'$lte': timestamp}
        #         },
        #         {
        #             '$set': pointing_with_pathing(doc)
        #         },
        #         upsert=True
        #     )
        #     for doc in documents
        # ]
        # if instructions:
        #     try:
        #         collection.bulk_write(instructions)
        #     except BulkWriteError:
        #         raise
        for doc in documents:
            try:
                collection.update_one({IDENT_KEY: doc.get(MONGODB_DB_COLLECTION_PK),
                                       'timestamp': {'$lte': timestamp}}, {'$set': pointing_with_pathing(doc)},
                                      upsert=True)
            except:
                ...


def pooler(processes, points):
    p = Pool(processes)
    p.map(for_pooling, points)
    p.close()
    p.join()


if __name__ == '__main__':
    args = settings.AXIS_POINTS
    pooler(8, args)
