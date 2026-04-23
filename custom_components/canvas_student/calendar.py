from datetime import datetime, timedelta
import datetime as dt_util
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([CanvasCalendarEntity(coordinator)])

class CanvasCalendarEntity(CoordinatorEntity, CalendarEntity):
    """Canvas Global Calendar."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Canvas Student Full"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_calendar_global"
        self._attr_icon = "mdi:database-import"

    @property
    def event(self) -> CalendarEvent | None:
        """Return the nearest upcoming event."""
        events = self._get_events(datetime.now(dt_util.timezone.utc), None)
        return events[0] if events else None

    async def async_get_events(self, hass, start_date, end_date) -> list[CalendarEvent]:
        """Return events for the requested UI window."""
        return self._get_events(start_date, end_date)

    def _get_events(self, start_filter, end_filter) -> list[CalendarEvent]:
        """Process coordinator data without internal date restrictions."""
        if not self.coordinator.data:
            return []

        evs = []
        for item in self.coordinator.data:
            raw_start = item.get("start_at") or item.get("end_at")
            raw_end = item.get("end_at") or item.get("start_at")
            
            if not raw_start:
                continue

            try:
                st = datetime.fromisoformat(raw_start.replace("Z", "+00:00"))
                en = datetime.fromisoformat(raw_end.replace("Z", "+00:00"))
                
                # Due date duration fix
                if st == en:
                    st = st - timedelta(minutes=30)

                # We only filter by what the Home Assistant UI asks for
                if start_filter and en < start_filter:
                    continue
                if end_filter and st > end_filter:
                    continue

                evs.append(CalendarEvent(
                    summary=item.get("title", "Canvas Item"),
                    start=st,
                    end=en,
                    description=f"Context: {item.get('context_name', 'Canvas')}",
                    location=item.get("html_url", "")
                ))
            except:
                continue
            
        evs.sort(key=lambda x: x.start)
        return evs