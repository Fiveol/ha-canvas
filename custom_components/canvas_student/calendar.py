from datetime import timedelta
import homeassistant.util.dt as dt_util

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Canvas calendar platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    user_name = coordinator.data.get("name", "Student")
    
    # 1. Start with the Master "All assignments" calendar
    entities = [CanvasCalendarEntity(coordinator, "all", f"{user_name} Calendar")]

    # 2. Add calendars for each active course found in the data
    for course in coordinator.data.get("courses", []):
        if not isinstance(course, dict) or "id" not in course:
            continue
            
        course_name = course.get("course_code") or course.get("name")
        # Skip courses that have no identifiable name
        if not course_name:
            continue
            
        entities.append(
            CanvasCalendarEntity(
                coordinator, 
                course["id"], 
                f"{user_name} {course_name} Calendar"
            )
        )

    async_add_entities(entities)

class CanvasCalendarEntity(CoordinatorEntity, CalendarEntity):
    """Representation of a Canvas Assignment Calendar."""

    _attr_attribution = "Data provided by Canvas LMS"

    def __init__(self, coordinator, course_id, name):
        """Initialize the Canvas Calendar."""
        super().__init__(coordinator)
        self._course_id = course_id
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_cal_{course_id}"
        self._attr_icon = "mdi:school"

    @property
    def device_info(self):
        """Group all calendars under a single Canvas 'Service' device."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": f"Canvas: {self.coordinator.data.get('name')}",
            "manufacturer": "Canvas LMS",
            "entry_type": "service",
        }

    def _get_events(self) -> list[CalendarEvent]:
        """Filter and convert coordinator data into HA CalendarEvents."""
        all_data = self.coordinator.data.get("events", [])
        events = []
        
        for item in all_data:
            # We only want to display assignments
            if "assignment" not in item:
                continue
                
            # If this entity is for a specific course, skip items from other courses
            if self._course_id != "all":
                if item.get("context_code") != f"course_{self._course_id}":
                    continue

            # Get the due date (Canvas uses end_at for assignments)
            due_at = item.get("end_at")
            if not due_at:
                continue

            # Robust timezone parsing using HA utility
            start_dt = dt_util.parse_datetime(due_at)
            if not start_dt:
                continue
            
            # Format points string safely
            points = item.get("assignment", {}).get("points_possible")
            points_str = f"\nPoints: {points}" if points is not None else ""
            
            events.append(
                CalendarEvent(
                    summary=item.get("title", "Assignment"),
                    start=start_dt,
                    end=start_dt, # Assignments are usually point-in-time
                    description=f"Course: {item.get('context_name')}{points_str}",
                    location=item.get("html_url", ""),
                )
            )
        
        # Sort by date
        events.sort(key=lambda x: x.start)
        return events

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event for the 'Next Event' sensor."""
        events = self._get_events()
        return events[0] if events else None

    async def async_get_events(self, hass, start_date, end_date) -> list[CalendarEvent]:
        """Return calendar events for the UI dashboard."""
        # Note: We return all fetched events here. HA UI handles further filtering.
        return self._get_events()