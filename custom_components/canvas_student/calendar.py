from datetime import datetime
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

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        if not self.coordinator.data:
            return None
            
        # Get the first assignment from our sorted list
        events = self._get_events()
        return events[0] if events else None

    async def async_get_events(self, hass, start_date, end_date) -> list[CalendarEvent]:
        """Return calendar events between two dates for the UI."""
        return self._get_events()

    def _get_events(self) -> list[CalendarEvent]:
        """Helper to convert API data into Home Assistant CalendarEvents."""
        events = []
        for item in self.coordinator.data:
            # We only want assignments with due dates
            if "assignment" not in item:
                continue
                
            due_at = item.get("end_at")
            if not due_at:
                continue

            # Convert Canvas ISO timestamp to datetime
            # Canvas uses Z (UTC), HA expects datetime objects
            start_dt = datetime.fromisoformat(due_at.replace("Z", "+00:00"))
            
            events.append(
                CalendarEvent(
                    summary=item.get("title"),
                    start=start_dt,
                    end=start_dt, # Assignments are usually a single point in time
                    description=f"Course: {item.get('context_name')}\nPoints: {item.get('assignment', {}).get('points_possible')}",
                    location=item.get("html_url"),
                )
            )
        return events