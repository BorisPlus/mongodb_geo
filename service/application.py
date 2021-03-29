#!/usr/bin/python3
from dummy_wsgi_framework.core.dispatchers import get_controller_response
from service import config as app_config


def application(environ, start_response):
    return get_controller_response(environ, start_response, app_config)
