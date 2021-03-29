#!/usr/bin/python3
import os

APP_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_ROOT_DIR_NAME = os.path.basename(APP_ROOT_DIR)
APP_NAME = 'MongoDB Geo'
APP_VIEWS_DIR = os.path.join(APP_ROOT_DIR, 'views')
APP_CONTROLLERS_DIR = os.path.join(APP_ROOT_DIR, 'controllers')
