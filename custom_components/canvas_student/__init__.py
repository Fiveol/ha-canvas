import datetime
import logging
import aiohttp
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_BASE_URL, CONF_ACCESS_TOKEN, LOGGER

PLATFORMS = ["calendar"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Canvas Student from a config entry."""
    
    async def async_update_data():
        """Fetch data from Canvas API for the current school year."""
        base_url = entry.data[CONF_BASE_URL].rstrip("/")
        token = entry.data[CONF_ACCESS_TOKEN]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Calculate School Year boundaries
        now = datetime.datetime.now()
        current_year = now.year
        
        # Rule: From June 1st onwards, look ahead to the NEXT August.
        # Otherwise, look at the current academic year ending this August.
        if now.month >= 6:
            start_date = f"{current_year}-09-01" # Next school year start
            end_date = f"{current_year + 1}-08-31"
            # To keep the "current" late-spring/summer stuff visible:
            start_date = f"{current_year - 1}-09-01" 
        else:
            start_date = f"{current_year - 1}-09-01"
            end_date = f"{current_year}-08-31"

        params = {
            "type": "assignment",
            "start_date": start_date,
            "end_date": end_date,
            "per_page": 100 
        }
        
        async with aiohttp.ClientSession() as session:
            url = f"{base_url}/api/v1/calendar_events"
            try:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Canvas API error: {response.status}")
                    return await response.json()
            except Exception as err:
                raise UpdateFailed(f"Error communicating with Canvas: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(hours=6),
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok