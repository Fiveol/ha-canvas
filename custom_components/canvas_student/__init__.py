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
    """Set up Canvas Student."""
    
    async def async_update_data():
        base_url = entry.data[CONF_BASE_URL].rstrip("/")
        token = entry.data[CONF_ACCESS_TOKEN]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Determine dates
        now = datetime.datetime.now()
        if now.month >= 6:
            start_date, end_date = f"{now.year-1}-09-01", f"{now.year+1}-08-31"
        else:
            start_date, end_date = f"{now.year-1}-09-01", f"{now.year}-08-31"

        async with aiohttp.ClientSession() as session:
            # 1. GET COURSE CONTEXT CODES (Crucial for seeing assignments)
            courses = []
            async with session.get(f"{base_url}/api/v1/courses", headers=headers) as resp:
                if resp.status == 200:
                    course_data = await resp.json()
                    courses = [f"course_{c['id']}" for c in course_data if 'id' in c]
            
            # 2. FETCH CALENDAR EVENTS
            all_events = []
            url = f"{base_url}/api/v1/calendar_events"
            params = {
                "type": "assignment",
                "start_date": start_date,
                "end_date": end_date,
                "per_page": 100,
                "context_codes[]": courses + ["user_self"] # Include courses + personal
            }

            curr_url = url
            while curr_url:
                async with session.get(curr_url, headers=headers, params=params if curr_url == url else None) as resp:
                    if resp.status != 200:
                        LOGGER.error("Canvas API Error: %s", resp.status)
                        break
                    
                    batch = await resp.json()
                    all_events.extend(batch)
                    
                    # Pagination logic
                    curr_url = None
                    links = resp.headers.get("Link", "")
                    if 'rel="next"' in links:
                        parts = links.split(",")
                        for part in parts:
                            if 'rel="next"' in part:
                                curr_url = part.split(";")[0].strip("<> ")

            LOGGER.info("Canvas: Successfully synced %s assignments", len(all_events))
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
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok