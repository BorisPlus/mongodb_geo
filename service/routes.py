#!/usr/bin/python3
from dummy_wsgi_framework.core.routes import DEFAULT

routes_of_uri_regexps = \
    dict(
        uri_regexp='^/index/$',
        controller='index.py'
    ), \
    dict(
        uri_regexp='^(/get_data/\?(geo_object_view=[a-z]*)&(north_east_lat=\-?\d*\.*\d*)&(north_east_lon=\-?\d*\.*\d*)&(south_west_lat=\-?\d*\.*\d*)&(south_west_lon=\-?\d*\.*\d*)/)$',
        controller='get_data.py'
    ), \
    dict(  #
        uri_regexp='^/circle/$',
        controller='circle.py'
    ), \
    dict(
        uri_regexp='^(/get_near_by/\?(lat=\-?\d*\.*\d*)&(lon=\-?\d*\.*\d*)&(distance=\-?\d*\.*\d*)/)$',
        controller='get_near_by.py'
    ), \
    dict(
        uri_regexp='^/about/$',
        controller='about.py'),\
    dict(
        uri_regexp=DEFAULT,
        controller='index.py'), \
    dict(
        uri_regexp='.*',
        controller='index.py'),
