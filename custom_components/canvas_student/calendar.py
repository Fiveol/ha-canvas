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
        self._attr_icon = "mdi:school-outline"

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event from the list."""
        events = self._get_events()
        if not events:
            return None
        
        now = datetime.now(dt_util.timezone.utc)
        future_events = [e for e in events if e.start >= now]
        return future_events[0] if future_events else None

    async def async_get_events(self, hass, start_date, end_date) -> list[CalendarEvent]:
        """Return calendar events for the UI."""
        # The UI provides its own window, but we already have the data
        return self._get_events()

    def _get_events(self) -> list[CalendarEvent]:
        """Helper to convert API data into Home Assistant CalendarEvents."""
        if not self.coordinator.data:
            return []

        calendar_events = []
        for item in self.coordinator.data:
            # We specifically want assignments
            if "assignment" not in item and "assignment_id" not in item:
                continue
                
            due_at_str = item.get("end_at") or item.get("start_at")
            if not due_at_str:
                continue

            try:
                # Convert Canvas UTC (Z) to HA localized datetime
                start_dt = datetime.fromisoformat(due_at_str.replace("Z", "+00:00"))
                
                calendar_events.append(
                    CalendarEvent(
                        summary=item.get("title", "Assignment"),
                        start=start_dt - timedelta(minutes=30), # 30 min duration
                        end=start_dt,
                        description=f"Course: {item.get('context_name')}\n{item.get('html_url')}",
                        location=item.get("context_name"),
                    )
                )
            except Exception:
                continue

        # Sort so the UI and next_event logic works correctly
        calendar_events.sort(key=lambda x: x.start)
        return calendar_events