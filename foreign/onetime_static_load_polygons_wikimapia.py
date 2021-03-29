import requests
import pymongo
from pymongo.errors import WriteError
from any import (
    IDENT_KEY,
)
from common import base_config

MONGODB_DB_COLLECTION_NAME = 'geo_wikimapia_polygons'
MONGODB_DB_COLLECTION_PK = 'id'
POLYGON_KEY = 'area'


def local_print(*args, **kwargs):
    if __name__ == '__main__':
        print(*args, **kwargs, sep='\t')


def get_data(se_lat, se_lon, nw_lat, nw_lon, page, api_key, category):
    link = (
        'http://api.wikimapia.org/?function=box'
        f'&category={category}'
        '&count=50'
        f'&page={page}'
        f'&bbox={se_lat},{se_lon},{nw_lat},{nw_lon}'
        '&format=json'
    )
    # local_print(link)
    response = requests.get(f'{link}&key={api_key}')
    if response.ok:
        dict_data = response.json()
        return dict_data.get('folder', [])
    return []


def polygonize(doc):
    polygon = dict()
    if doc.get("polygon"):
        polygon[POLYGON_KEY] = dict(type="Polygon", coordinates=[
            [
                [point.get('x'), point.get('y'), ] for point in doc.get("polygon", [])
            ] + [
                [doc.get("polygon")[0].get('x'), doc.get("polygon")[0].get('y'), ]
            ]
        ])
    return {
        **doc,
        **polygon,
        IDENT_KEY: doc.get(MONGODB_DB_COLLECTION_PK)
    }


def save_data(documents):
    with pymongo.MongoClient(base_config.MONGODB_CONNECTION_STRING) as client:
        collection = client[base_config.MONGODB_DB_NAME][MONGODB_DB_COLLECTION_NAME]
        for doc in documents:
            try:
                collection.update_one({IDENT_KEY: doc.get('id')}, {'$set': polygonize(doc)},upsert=True)
            except WriteError:
                ...


if __name__ == '__main__':
    # WikiMapia Api Token
    # api_key = '220E50EF-63FD0DFD-28E147AD-48A0E28A-D2D346F2-84C1395C-0A972683-159EACBC'
    api_key = '220E50EF-1F0C1A61-EB9903DC-66AE729D-6D09C1D9-2FDF4C86-DD330B60-56AF1A6'

    #
    se_lat_ = 29.88418579101563
    se_lon_ = 59.79579845298599
    nw_lat_ = 30.775451660156254
    nw_lon_ = 60.16269279790754
    #
    category = 17

    for page in range(100):
        docs = get_data(se_lat_, se_lon_, nw_lat_, nw_lon_, page + 1, api_key, category)
        if not len(docs):
            local_print(f'Max page {page} with some data')
            break
        local_print(f'Page {page + 1} has docs count {len(docs)}')
        save_data(docs)
