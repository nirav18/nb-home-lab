"""Nautobot development configuration file."""

# pylint: disable=invalid-envvar-default
import os
import sys

from nautobot.core.settings import *  # noqa: F403  # pylint: disable=wildcard-import,unused-wildcard-import
from nautobot.core.settings_funcs import is_truthy, parse_redis_connection

#
# Debug
#

# DEBUG = is_truthy(os.getenv("NAUTOBOT_DEBUG", True))

# TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"

#
# Logging
#

LOG_LEVEL = "INFO"

#
# Redis
#

# Redis Cacheops
CACHEOPS_REDIS = parse_redis_connection(redis_database=1)

#
# Celery settings are not defined here because they can be overloaded with
# environment variables. By default they use `CACHES["default"]["LOCATION"]`.
#

# Enable installed plugins. Add the name of each plugin to the list.
# PLUGINS = ["nautobot_example_plugin"]
PLUGINS = []

# Plugins configuration settings. These settings are used by various plugins that the user may have installed.
# Each key in the dictionary is the name of an installed plugin and its value is a dictionary of settings.
PLUGINS_CONFIG = {
    "nautobot_example_plugin": {},
}

# EXTRA_JOBS = [
#     "/opt/nautobot/jobs",
# ]

# STATIC_ROOT is the directory from which static files will be served.
STATIC_URL = "/static/"
STATIC_ROOT = "/opt/nautobot/static"


# Secret key (KEEP THIS SECRET!)
SECRET_KEY = os.getenv('NAUTOBOT_SECRET_KEY', 'superstarsecretkey')