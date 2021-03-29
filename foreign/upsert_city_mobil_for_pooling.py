from common import base_config
from source_city_mobil import get_data as get_data_from_city_mobil
from any import IDENT_KEY
from upsert_city_mobil import (
    MONGODB_DB_COLLECTION_NAME,
    MONGODB_DB_COLLECTION_PK
)
import pymongo
from pymongo import UpdateOne
import time
import settings
from multiprocessing import Pool
from upsert_city_mobil import city_mobil_pointing


def local_print(*args, **kwargs):
    if __name__ == '__main__':
        print(*args, **kwargs, sep='\t')


def for_pooling(lan_lot):
    lan, lot = lan_lot
    timestamp, documents = get_data_from_city_mobil((lan, lot))

    local_print(timestamp, len(documents))

    with pymongo.MongoClient(base_config.MONGODB_CONNECTION_STRING) as client:
        collection = client[base_config.MONGODB_DB_NAME][MONGODB_DB_COLLECTION_NAME]
        instructions = [
            UpdateOne(
                {
                    IDENT_KEY: doc[MONGODB_DB_COLLECTION_PK],
                    'timestamp': {'$lte': timestamp}
                },
                {
                    '$set': city_mobil_pointing(timestamp, doc)
                },
                upsert=True
            )
            for doc in documents
        ]
        if instructions:
            collection.bulk_write(instructions)


def pooler(processes, points):
    p = Pool(processes)
    p.map(for_pooling, points)
    p.close()
    p.join()


if __name__ == '__main__':
    # from common import base_config
    # for_pooling((base_config.LON, base_config.LAT,))
    #
    start_at = time.time()
    pooler(8, settings.AXIS_POINTS)
    local_print(len(settings.AXIS_POINTS), time.time() - start_at)
