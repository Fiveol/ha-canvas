from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Canvas sensor from a config entry."""
    # Retrieve the coordinator we stored in __init__.py
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Add the sensor to Home Assistant
    async_add_entities([CanvasAssignmentsSensor(coordinator)])

class CanvasAssignmentsSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Canvas Assignments sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Canvas Assignments"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_assignments"
        self._attr_icon = "mdi:school"

    @property
    def state(self):
        """Return the number of upcoming assignments."""
        if self.coordinator.data is None:
            return 0
        # Filter the data to count only items of type 'assignment'
        assignments = [item for item in self.coordinator.data if item.get("type") == "assignment"]
        return len(assignments)

    @property
    def extra_state_attributes(self):
        """Return detailed assignment data."""
        if self.coordinator.data is None:
            return {}
        
        # Pass the raw list of upcoming events as an attribute
        return {
            "upcoming_events": self.coordinator.data
        }