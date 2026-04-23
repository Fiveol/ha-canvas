import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_BASE_URL, CONF_ACCESS_TOKEN

class CanvasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Canvas Student."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # We will add validation logic here later
            return self.async_create_entry(title="Canvas Student", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_BASE_URL): str,
                    vol.Required(CONF_ACCESS_TOKEN): str,
                }
            ),
            errors=errors,
        )