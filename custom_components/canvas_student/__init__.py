import datetime
import logging
import aiohttp
import asyncio
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_BASE_URL, CONF_ACCESS_TOKEN, LOGGER

PLATFORMS = ["calendar"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Canvas Student from a config entry."""
    
    async def async_update_data():
        """Fetch all assignments for the calculated school year range."""
        base_url = entry.data[CONF_BASE_URL].rstrip("/")
        token = entry.data[CONF_ACCESS_TOKEN]
        headers = {"Authorization": f"Bearer {token}"}
        
        now = datetime.datetime.now()
        
        # --- SCHOOL YEAR LOGIC ---
        # September 1st to August 31st
        if now.month >= 9:
            # SEPT - DEC: Load current year only
            start_dt = datetime.date(now.year, 9, 1)
            end_dt = datetime.date(now.year + 1, 8, 31)
        elif now.month >= 6:
            # JUNE - AUG: Load previous year AND next year (2 year span)
            start_dt = datetime.date(now.year - 1, 9, 1)
            end_dt = datetime.date(now.year + 1, 8, 31)
        else:
            # JAN - MAY: Load current academic year (started last Sept)
            start_dt = datetime.date(now.year - 1, 9, 1)
            end_dt = datetime.date(now.year, 8, 31)

        num_days = (end_dt - start_dt).days
        # Goal: 128 events per day max capacity
        total_capacity = num_days * 128 
        
        LOGGER.info("Canvas: Loading %s days of assignments (Limit: %s)", num_days, total_capacity)

        all_events = []
        # Canvas API endpoint for multiple items
        url = f"{base_url}/api/v1/calendar_events"
        params = {
            "type": "assignment",
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "per_page": 100  # Request in blocks of 100
        }

        async with aiohttp.ClientSession() as session:
            next_url = url
            while next_url and len(all_events) < total_capacity:
                try:
                    async with session.get(next_url, headers=headers, params=params if next_url == url else None) as response:
                        if response.status != 200:
                            LOGGER.error("Canvas API Error %s", response.status)
                            break
                        
                        data = await response.json()
                        all_events.extend(data)
                        
                        # --- PAGINATION LOGIC ---
                        # Canvas sends a 'Link' header for the next page
                        next_url = None
                        links = response.headers.get("Link", "")
                        if 'rel="next"' in links:
                            # Extract the URL between < and >
                            parts = links.split(",")
                            for part in parts:
                                if 'rel="next"' in part:
                                    next_url = part.split(";")[0].strip("<> ")
                except Exception as err:
                    LOGGER.error("Fetch failed: %s", err)
                    break
            
            LOGGER.info("Canvas Sync Complete: %s assignments found", len(all_events))
            return all_events

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