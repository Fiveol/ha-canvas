import voluptuous as vol
import aiohttp
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_BASE_URL, CONF_ACCESS_TOKEN, LOGGER

class CanvasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def _validate_canvas_connection(self, base_url, token):
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {token}"}
                url = f"{base_url.rstrip('/')}/api/v1/users/self/profile"
                
                async with session.get(url, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        return None
                    if resp.status == 401:
                        return "invalid_auth"
                    return "cannot_connect"
        except Exception:
            return "cannot_connect"

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            error = await self._validate_canvas_connection(
                user_input[CONF_BASE_URL], user_input[CONF_ACCESS_TOKEN]
            )
            if not error:
                return self.async_create_entry(title="Canvas Student", data=user_input)
            errors["base"] = error

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_BASE_URL): str,
                vol.Required(CONF_ACCESS_TOKEN): str,
            }),
            errors=errors,
            description_placeholders={
                "documentation_url": "https://github.com/Fiveol/ha-canvas"
            },
        )

    async def async_step_reconfigure(self, user_input=None):
        errors = {}
        entry = self._get_reconfigure_entry()
        
        if user_input is not None:
            error = await self._validate_canvas_connection(
                user_input[CONF_BASE_URL], user_input[CONF_ACCESS_TOKEN]
            )
            if not error:
                return self.async_update_reload_and_abort(
                    entry, data={**entry.data, **user_input}
                )
            errors["base"] = error

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema({
                vol.Required(CONF_BASE_URL, default=entry.data.get(CONF_BASE_URL)): str,
                vol.Required(CONF_ACCESS_TOKEN, default=entry.data.get(CONF_ACCESS_TOKEN)): str,
            }),
            errors=errors,
            description_placeholders={
                "documentation_url": "https://github.com/Fiveol/ha-canvas"
            },
        )
