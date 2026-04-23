from datetime import datetime, timedelta
import datetime as dt_util
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([CanvasCalendarEntity(coordinator)])

class CanvasCalendarEntity(CoordinatorEntity, CalendarEntity):
    """Canvas Assignment Calendar."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Canvas Assignments"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_calendar"
        self._attr_icon = "mdi:school"

    @property
    def event(self) -> CalendarEvent | None:
        events = self._get_events()
        if not events: return None
        now = datetime.now(dt_util.timezone.utc)
        future = [e for e in events if e.start >= now]
        return future[0] if future else None

    async def async_get_events(self, hass, start_date, end_date) -> list[CalendarEvent]:
        return self._get_events()

    def _get_events(self) -> list[CalendarEvent]:
        if not self.coordinator.data: return []
        evs = []
        for item in self.coordinator.data:
            due = item.get("end_at") or item.get("start_at")
            if not due: continue
            try:
                start_dt = datetime.fromisoformat(due.replace("Z", "+00:00"))
                evs.append(CalendarEvent(
                    summary=item.get("title", "Assignment"),
                    start=start_dt - timedelta(minutes=30),
                    end=start_dt,
                    description=f"Course: {item.get('context_name')}",
                    location=item.get("html_url", "")
                ))
            except: continue
        evs.sort(key=lambda x: x.start)
        return evs