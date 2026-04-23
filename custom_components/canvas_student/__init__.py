from datetime import timedelta
import logging
import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_BASE_URL, CONF_ACCESS_TOKEN, LOGGER

PLATFORMS = ["calendar"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Canvas Student from a config entry."""
    
    async def async_update_data():
        """Fetch data from Canvas API."""
        base_url = entry.data[CONF_BASE_URL].rstrip("/")
        token = entry.data[CONF_ACCESS_TOKEN]
        headers = {"Authorization": f"Bearer {token}"}
        
        async with aiohttp.ClientSession() as session:
            try:
                # 1. Fetch User Profile for the name
                async with session.get(f"{base_url}/api/v1/users/self/profile", headers=headers) as resp:
                    profile = await resp.json()
                
                # 2. Fetch Courses
                async with session.get(f"{base_url}/api/v1/courses?enrollment_state=active", headers=headers) as resp:
                    courses = await resp.json()

                # 3. Fetch Upcoming Events
                async with session.get(f"{base_url}/api/v1/users/self/upcoming_events", headers=headers) as resp:
                    events = await resp.json()

                return {
                    "name": profile.get("short_name") or profile.get("name", "Student"),
                    "courses": courses,
                    "events": events
                }
            except Exception as err:
                raise UpdateFailed(f"Error communicating with Canvas: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(minutes=15),
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True