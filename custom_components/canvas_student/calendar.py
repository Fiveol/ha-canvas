from datetime import datetime, timedelta
import datetime as dt_util
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Canvas calendar platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([CanvasCalendarEntity(coordinator)])

class CanvasCalendarEntity(CoordinatorEntity, CalendarEntity):
    """Representation of a Canvas Assignment Calendar."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Canvas Assignments"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_calendar"
        self._attr_icon = "mdi:calendar-check"

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        events = self._get_events()
        if not events:
            return None
        
        # upcoming_events is already sorted by Canvas
        return events[0]

    async def async_get_events(self, hass, start_date, end_date) -> list[CalendarEvent]:
        """Return calendar events."""
        return self._get_events()

    def _get_events(self) -> list[CalendarEvent]:
        """Convert Canvas data into Home Assistant CalendarEvents."""
        if not self.coordinator.data:
            return []

        events = []
        for item in self.coordinator.data:
            # Get the due date/time
            due_at = item.get("end_at") or item.get("start_at")
            if not due_at:
                continue

            try:
                # Convert Canvas ISO (UTC) to datetime
                start_dt = datetime.fromisoformat(due_at.replace("Z", "+00:00"))
                
                events.append(
                    CalendarEvent(
                        summary=item.get("title", "Assignment"),
                        start=start_dt - timedelta(minutes=30),
                        end=start_dt,
                        description=f"Course: {item.get('context_name')}",
                        location=item.get("html_url", ""),
                    )
                )
            except Exception:
                continue
                
        return events