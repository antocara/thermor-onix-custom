"""Select platform for the Thermor Onix DHW Plus integration."""
from __future__ import annotations

import logging
from typing import Any

from pyoverkiz.models import Device

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CMD_SET_OPERATING_RANGE,
    DOMAIN,
    RANGE_24H,
    RANGE_OFF_PEAK,
    RANGE_PROGRAMMED,
    STATE_OPERATING_RANGE,
)
from .coordinator import ThermorDataUpdateCoordinator
from .entity import ThermorOnixEntity

_LOGGER = logging.getLogger(__name__)

OPTION_24H = "24h Continuous"
OPTION_PROGRAMMED = "Programmed Slots"
OPTION_OFF_PEAK = "Off-Peak Hours (HC)"

RANGE_TO_OPTION = {
    RANGE_24H: OPTION_24H,
    RANGE_PROGRAMMED: OPTION_PROGRAMMED,
    RANGE_OFF_PEAK: OPTION_OFF_PEAK,
    "pacHC_elecHC": OPTION_OFF_PEAK,
    "pac24h_elecProg": OPTION_PROGRAMMED,
}

OPTION_TO_RANGE = {
    OPTION_24H: RANGE_24H,
    OPTION_PROGRAMMED: RANGE_PROGRAMMED,
    OPTION_OFF_PEAK: RANGE_OFF_PEAK,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select entities from a config entry."""
    coordinator: ThermorDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    if coordinator.main_device:
        async_add_entities(
            [ThermorOperatingRangeSelect(coordinator, coordinator.main_device)]
        )


class ThermorOperatingRangeSelect(ThermorOnixEntity, SelectEntity):
    """Select entity to control the internal operating range and scheduling mode."""

    _attr_options = [OPTION_24H, OPTION_PROGRAMMED, OPTION_OFF_PEAK]
    _attr_icon = "mdi:calendar-clock"

    def __init__(
        self,
        coordinator: ThermorDataUpdateCoordinator,
        device: Device,
    ) -> None:
        """Initialize the operating range selector."""
        super().__init__(coordinator, device, "operating_range")
        self._attr_name = "Operating Schedule Mode"

    @property
    def current_option(self) -> str | None:
        """Return the current operating mode option."""
        raw_val = self.get_state(STATE_OPERATING_RANGE)
        return RANGE_TO_OPTION.get(str(raw_val), OPTION_24H)

    async def async_select_option(self, option: str) -> None:
        """Send the updated operating range mode to the water heater."""
        target_range = OPTION_TO_RANGE.get(option, RANGE_24H)
        _LOGGER.info("Setting Thermor Onix operating range to: %s (%s)", option, target_range)
        await self.coordinator.async_execute_command(
            self._device.device_url,
            CMD_SET_OPERATING_RANGE,
            [target_range],
        )
