from datetime import datetime
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Canvas calendar platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    user_name = coordinator.data.get("name", "Student")

    # 1. Create the Master Calendar
    entities.append(CanvasCalendarEntity(coordinator, "all", f"{user_name} Calendar"))

    # 2. Create Course-Specific Calendars
    for course in coordinator.data.get("courses", []):
        if isinstance(course, dict) and "id" in course:
            course_name = course.get("course_code") or course.get("name")
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

    def __init__(self, coordinator, course_id, name):
        super().__init__(coordinator)
        self._course_id = course_id
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_cal_{course_id}"

    def _get_events(self) -> list[CalendarEvent]:
        """Filter and convert API data into Home Assistant CalendarEvents."""
        all_data = self.coordinator.data.get("events", [])
        events = []
        
        for item in all_data:
            if "assignment" not in item:
                continue
                
            # If this is a course-specific calendar, filter by course ID
            # Canvas context_code looks like 'course_12345'
            if self._course_id != "all":
                if item.get("context_code") != f"course_{self._course_id}":
                    continue

            due_at = item.get("end_at")
            if not due_at:
                continue

            start_dt = datetime.fromisoformat(due_at.replace("Z", "+00:00"))
            
            events.append(
                CalendarEvent(
                    summary=item.get("title"),
                    start=start_dt,
                    end=start_dt,
                    description=f"Course: {item.get('context_name')}\nPoints: {item.get('assignment', {}).get('points_possible')}",
                    location=item.get("html_url"),
                )
            )
        return events

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        events = self._get_events()
        return events[0] if events else None

    async def async_get_events(self, hass, start_date, end_date) -> list[CalendarEvent]:
        """Return calendar events."""
        return self._get_events()