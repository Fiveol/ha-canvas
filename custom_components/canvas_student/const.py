"""Constants for the Canvas Student integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "canvas_student"
CONF_BASE_URL = "base_url"
CONF_ACCESS_TOKEN = "access_token"