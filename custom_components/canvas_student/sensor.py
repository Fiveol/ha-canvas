from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Canvas Grade sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Create a sensor for every course in the data
    entities = []
    for course in coordinator.data["courses"]:
        # Only add sensors for courses that have a name and aren't restricted
        if "name" in course and "id" in course:
            entities.append(CanvasGradeSensor(coordinator, course))
            
    async_add_entities(entities)

class CanvasGradeSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Canvas Course Grade sensor."""

    def __init__(self, coordinator, course):
        super().__init__(coordinator)
        self._course_id = course["id"]
        self._attr_name = f"{course['name']} Grade"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_grade_{self._course_id}"
        
        # This makes it pretty in the UI with a % sign and a graph
        self._attr_native_unit_of_measurement = "%"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the current percentage grade."""
        # Find this specific course in the updated coordinator data
        for course in self.coordinator.data["courses"]:
            if course.get("id") == self._course_id:
                enrollments = course.get("enrollments", [])
                if enrollments:
                    # 'computed_current_score' is the % grade
                    return enrollments[0].get("computed_current_score")
        return None

    @property
    def extra_state_attributes(self):
        """Return additional data like the letter grade."""
        for course in self.coordinator.data["courses"]:
            if course.get("id") == self._course_id:
                enrollments = course.get("enrollments", [])
                if enrollments:
                    return {
                        "letter_grade": enrollments[0].get("computed_current_grade"),
                        "final_score": enrollments[0].get("computed_final_score"),
                    }
        return {}