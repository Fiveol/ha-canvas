import logging

# The domain of your integration. Should be the same as the folder name.
DOMAIN = "canvas_student"

# Setup the logger for the integration
LOGGER = logging.getLogger(__package__)

# Configuration constants
CONF_BASE_URL = "base_url"
CONF_ACCESS_TOKEN = "access_token"