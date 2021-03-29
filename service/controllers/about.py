from base_config import (
    MONGODB_CONNECTION_STRING,
    MONGODB_DB_NAME,
    MONGODB_DB_COLLECTIONS,
)
from service.config import APP_NAME


def get_response(environ, start_response, app_config):
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    return [bytes(
        (
            f"<tt>"
            f"Settings of app: {APP_NAME}<br/>"
            f"<br/>"
            f"MONGODB_CONNECTION_STRING = {MONGODB_CONNECTION_STRING}<br/>"
            f"MONGODB_DB_NAME = {MONGODB_DB_NAME}<br/>"
            f"MONGODB_DB_COLLECTIONS = {MONGODB_DB_COLLECTIONS}<br/>"
            f"<br/>"
            f"ILYA special for <a target='_blank' href='https://otus.ru/'>OTUS</a> NoSQL Course"
            f"</tt>"
        )
        , 'utf-8')]
