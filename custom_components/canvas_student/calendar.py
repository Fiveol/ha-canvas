from datetime import datetime, timedelta
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
        """Return the next upcoming event (closest to now)."""
        events = self._get_events()
        now = datetime.now(datetime.utcnow().astimezone().tzinfo)
        
        # Filter for events that haven't finished yet and pick the first
        future_events = [e for e in events if e.start >= now]
        return future_events[0] if future_events else None

    async def async_get_events(self, hass, start_date, end_date) -> list[CalendarEvent]:
        """Return calendar events for the UI within a specific window."""
        # The coordinator already has the full year; we just return them all
        # and Home Assistant UI will filter them for the current view.
        return self._get_events()

    def _get_events(self) -> list[CalendarEvent]:
        """Helper to convert API data into Home Assistant CalendarEvents."""
        if not self.coordinator.data:
            return []

        events = []
        for item in self.coordinator.data:
            # Check if this is an assignment
            if item.get("assignment") is None:
                continue
                
            # Canvas provides 'end_at' for assignment due dates
            due_at_str = item.get("end_at") or item.get("start_at")
            if not due_at_str:
                continue

            try:
                # Parse UTC string to datetime object
                start_dt = datetime.fromisoformat(due_at_str.replace("Z", "+00:00"))
                
                events.append(
                    CalendarEvent(
                        summary=item.get("title"),
                        start=start_dt - timedelta(minutes=30), # Show as a 30m block ending at due time
                        end=start_dt,
                        description=f"Course: {item.get('context_name')}\nURL: {item.get('html_url')}",
                        location=item.get("context_name"),
                    )
                )
            except (ValueError, TypeError):
                continue

        # Sort all events by date
        events.sort(key=lambda x: x.start)
        return events