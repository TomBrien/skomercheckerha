"""Sensor platform for Skomer."""

from __future__ import annotations


import datetime
import logging

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass

from homeassistant.core import HomeAssistant
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SkomerCheckerConfigEntry, SkomerUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "Data provided by FareHarbor"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: SkomerCheckerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Skomer Checker sensor platform."""

    entities: list[SensorEntity] = [SkomerSensor(config_entry.runtime_data.coordinator)]

    async_add_entities(entities)


class SkomerSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Skomer Checker sensor."""

    def __init__(self, instance: SkomerUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(instance)
        _LOGGER.debug("Trying to set up Skomer Checker Sensor")
        self._data = instance.data
        self._name = instance.name
        self._id = (
            f"next_{instance.entry.data['DAYS_TO_CHECK']}_days_"
            f"{instance.entry.data['MIN_AVAILABILITY']}_"
            f"{'people' if instance.entry.data['MIN_AVAILABILITY'] > 1 else 'person'}_"
            f"{'weekends' if instance.entry.data['ONLY_WEEKENDS'] else 'anyday'}"
        )
        self._entry = instance.entry

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the Unique ID of the sensor."""
        return self._id

    @property
    def native_value(self) -> datetime.date:
        """Return the state of the sensor."""
        return self._data["date"]

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the sensor."""
        return SensorDeviceClass.DATE

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return the state attributes of the sensor."""
        attrs = {ATTR_ATTRIBUTION: ATTRIBUTION}
        attrs["spaces_available"] = self._data["spaces_available"]
        attrs["spaces_required"] = self._entry.data["MIN_AVAILABILITY"]

        return attrs
