import logging
import aiohttp
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_BASE_URL, CONF_ACCESS_TOKEN, LOGGER

PLATFORMS = ["calendar"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Canvas Student - Unfiltered History."""
    
    async def async_update_data():
        base_url = entry.data[CONF_BASE_URL].rstrip("/")
        token = entry.data[CONF_ACCESS_TOKEN]
        headers = {"Authorization": f"Bearer {token}"}
        
        all_events = []
        url = f"{base_url}/api/v1/calendar_events"
        # No start/end dates = Everything
        params = {
            "per_page": 100,
            "all_events": "true"
        }

        async with aiohttp.ClientSession() as session:
            curr_url = url
            while curr_url and len(all_events) < 3000:
                async with session.get(curr_url, headers=headers, params=params if curr_url == url else None) as resp:
                    if resp.status != 200:
                        LOGGER.error("Canvas API Error: %s", resp.status)
                        break
                    
                    batch = await resp.json()
                    if not batch:
                        break
                        
                    all_events.extend(batch)
                    
                    # Follow the 'Link' header to the next page
                    curr_url = None
                    links = resp.headers.get("Link", "")
                    if 'rel="next"' in links:
                        parts = links.split(",")
                        for part in parts:
                            if 'rel="next"' in part:
                                curr_url = part.split(";")[0].strip("<> ")

            LOGGER.info("Canvas Total Dump: %s items fetched from all time", len(all_events))
            return all_events

    coordinator = DataUpdateCoordinator(
        hass, LOGGER, name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(hours=6),
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)