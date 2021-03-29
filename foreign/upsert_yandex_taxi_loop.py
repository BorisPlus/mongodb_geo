import time
import settings
from upsert_yandex_taxi_for_pooling import pooler


def local_print(*args, **kwargs):
    if __name__ == '__main__':
        print(*args, **kwargs, sep='\t')


if __name__ == '__main__':
    while True:
        start_at = time.time()
        pooler(8, settings.AXIS_POINTS)
        local_print(len(settings.AXIS_POINTS), time.time() - start_at)
