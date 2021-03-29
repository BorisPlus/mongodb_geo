from common import base_config
from source_city_mobil import get_data as get_data_from_city_mobil
from upsert_any_formatting import mongodb_upsert, pointing

MONGODB_DB_COLLECTION_NAME = 'geo_city_mobil'
MONGODB_DB_COLLECTION_PK = 'pk_id'


def city_mobil_pointing(timestamp, doc):
    return pointing(timestamp, doc, lon_field='ln', lat_field='lt',)


# It is not work in pool
@mongodb_upsert(
    base_config.MONGODB_CONNECTION_STRING,
    base_config.MONGODB_DB_NAME,
    MONGODB_DB_COLLECTION_NAME,
    MONGODB_DB_COLLECTION_PK,
    city_mobil_pointing)
def upsert_city_mobil(*args, **kwargs):
    return get_data_from_city_mobil(*args, **kwargs)


if __name__ == '__main__':
    upsert_city_mobil((base_config.LON, base_config.LAT,))

    # from multiprocessing import Pool
    # import time
    # import settings
    # from upsert_any_formatting import as_is
    # # AttributeError: Can't pickle local object...` when using multiprocessing
    # # https://github.com/pytorch/xla/issues/1554
    # start_at = time.time()
    # #
    # p = Pool(8)
    # p.map(upsert_city_mobil, settings.AXIS_POINTS)
    # p.close()
    # p.join()
    # #
    # print(len(settings.AXIS_POINTS), time.time() - start_at)
