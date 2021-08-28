import os
import json
from json import JSONDecodeError

from pathlib import Path

from route import RouteFactory
from threading import Lock

import logging
import logging.config as log_conf

logger = logging.getLogger('keepRoute')

APP_DIR = os.getenv('APPDATA')
ROUTE_FILE = os.path.join(APP_DIR, 'keep-route', 'route.json')
OPTION_FILE = os.path.join(APP_DIR, 'keep-route', 'option.json')
LOG_CONFIG = os.path.join(APP_DIR, 'keep-route', 'logging.conf')
LOG_FILE = os.path.join(APP_DIR, 'keep-route', 'keep-route.log')

DEFAULT_OPTIONS = {
    "interval_sec": 60,
}

os.makedirs(os.path.join(APP_DIR, 'keep-route'), exist_ok=True)

lock = Lock()

if Path(LOG_CONFIG).is_file():
    log_conf.fileConfig(LOG_CONFIG)

def routes():

    if Path(ROUTE_FILE).is_file():
        lock.acquire()
        with open(ROUTE_FILE) as f:
            routes = RouteFactory.create(f)
        lock.release()
    else:
        Path(ROUTE_FILE).touch()
        routes = []

    return routes

def save_routes(routes):
    if Path(ROUTE_FILE).is_file():
        lock.acquire()
        with open(ROUTE_FILE, "w") as f:
            _routes = []
            for route in routes:
                _routes.append(route.to_dict())
            json.dump(_routes, f)
        lock.release()

def options():

    options = DEFAULT_OPTIONS

    if Path(OPTION_FILE).is_file():
        lock.acquire()
        with open(OPTION_FILE) as f:
            try:
                options.update(json.load(f))
            except JSONDecodeError as e:
                pass
        lock.release()

    else:
        Path(OPTION_FILE).touch()

    return options

def save_options(options = DEFAULT_OPTIONS):
    options

    if Path(OPTION_FILE).is_file():
        lock.acquire()
        with open(OPTION_FILE, "w") as f:
            try:
                json.dump(options, f)
            except:
                pass
        lock.release()
