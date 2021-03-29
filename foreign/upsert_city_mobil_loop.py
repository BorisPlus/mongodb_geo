import time
import settings
from upsert_city_mobil_for_pooling import pooler
from upsert_city_mobil_delete_old_data import for_delete_all


def local_print(*args, **kwargs):
    if __name__ == '__main__':
        print(*args, **kwargs, sep='\t')


if __name__ == '__main__':
    while True:
        start_at = time.time()
        for_delete_all()
        pooler(8, settings.AXIS_POINTS)
        local_print(len(settings.AXIS_POINTS), time.time() - start_at)
