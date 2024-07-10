"""The Skomer Checker integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta, date
import datetime
from typing import Any

from dateutil import relativedelta
import logging


from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant


from skomerchecker import Checker

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


@dataclass
class SkomerData:
    """Data for Skomer Checker integration."""

    coordinator: SkomerUpdateCoordinator


type SkomerCheckerConfigEntry = ConfigEntry[SkomerData]


async def async_setup_entry(
    hass: HomeAssistant, entry: SkomerCheckerConfigEntry
) -> bool:
    """Set up Skomer Checker from a config entry."""

    coordinator = SkomerUpdateCoordinator(hass, Checker(), entry)

    _LOGGER.debug(f"In setup: {coordinator}")
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = SkomerData(coordinator)

    _LOGGER.debug(
        "After refresh, data in runtime is %s", entry.runtime_data.coordinator.data
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: SkomerCheckerConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


class SkomerUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Skomer data API."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: Checker,
        entry: SkomerCheckerConfigEntry,
    ) -> None:
        """Initialize."""
        self.api = api
        self.entry = entry
        self.id = (
            f"skomer-{self.entry.data['DAYS_TO_CHECK']}-"
            f"{self.entry.data['MIN_AVAILABILITY']}-"
            f"{'weekends' if self.entry.data['ONLY_WEEKENDS'] else 'anyday'}"
        )

        super().__init__(
            hass,
            _LOGGER,
            name=(
                f"{'Weekends' if self.entry.data['ONLY_WEEKENDS'] else 'Anyday'} "
                f"for {self.entry.data['MIN_AVAILABILITY']} "
                f"{'person' if self.entry.data['MIN_AVAILABILITY'] == 1 else 'people'} "
                f"in next {self.entry.data['DAYS_TO_CHECK']} days"
            ),
            update_interval=timedelta(minutes=15),
        )

    async def _async_update_data(self) -> dict:
        """Update data via library."""
        try:
            _LOGGER.debug("Trying to update data")
            today = date.today()
            day_of_month = today.day
            month_offset = 0
            data: list[dict] = []
            while len(data) < self.entry.data["DAYS_TO_CHECK"] + day_of_month:
                response = self.api.get_data(
                    today + relativedelta.relativedelta(months=month_offset)
                )
                if not response:
                    raise UpdateFailed("No data returned")

                for week in response["weeks"]:
                    for day in week["days"]:
                        if day["month"] == "current":
                            data += [day]
                month_offset += 1

        except Exception as error:
            raise UpdateFailed(error) from error

        for day in data[day_of_month : day_of_month + self.entry.data["DAYS_TO_CHECK"]]:
            if not day.get("is_bookable"):
                continue
            for aval in day["availabilities"]:
                if aval["bookable_capacity"] > self.entry.data["MIN_AVAILABILITY"]:
                    if not self.entry.data["ONLY_WEEKENDS"] or day["name"] in [
                        "Monday",  # Monday sailings only take place on bank holidays
                        "Saturday",
                        "Sunday",
                    ]:

                        _LOGGER.debug(
                            f"Found date: {self.data} with {aval['bookable_capacity']} "
                            "spaces available"
                        )
                        return {
                            "date": datetime.datetime.strptime(
                                day["at"], "%Y-%m-%d"
                            ).date(),
                            "spaces_available": aval["bookable_capacity"],
                        }
        _LOGGER.debug("No date found meeting requirements")
        return {"date": None, "spaces_available": 0}
