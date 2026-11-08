"""Number platform for the Thermor Onix DHW Plus integration."""
from __future__ import annotations

import logging

from pyoverkiz.models import Device

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CMD_SET_EXPECTED_SHOWERS,
    DOMAIN,
    STATE_SHOWERS_EXPECTED,
)
from .coordinator import ThermorDataUpdateCoordinator
from .entity import ThermorOnixEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities from a config entry."""
    coordinator: ThermorDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    if coordinator.main_device:
        async_add_entities(
            [ThermorExpectedShowersNumber(coordinator, coordinator.main_device)]
        )


class ThermorExpectedShowersNumber(ThermorOnixEntity, NumberEntity):
    """Number slider to adjust the target number of showers to heat."""

    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 1.0
    _attr_native_max_value = 5.0
    _attr_native_step = 1.0
    _attr_native_unit_of_measurement = "showers"
    _attr_icon = "mdi:shower"

    def __init__(
        self,
        coordinator: ThermorDataUpdateCoordinator,
        device: Device,
    ) -> None:
        """Initialize the expected showers number entity."""
        super().__init__(coordinator, device, "expected_showers")
        self._attr_name = "Expected Showers"

    @property
    def native_value(self) -> float | None:
        """Return the target shower count currently programmed."""
        val = self.get_state(STATE_SHOWERS_EXPECTED)
        if val is not None:
            try:
                return float(val)
            except (ValueError, TypeError):
                pass
        return 1.0

    async def async_set_native_value(self, value: float) -> None:
        """Send the updated target shower count to the Thermor cloud."""
        int_val = int(value)
        _LOGGER.info("Setting expected showers on Thermor Onix to: %d", int_val)
        await self.coordinator.async_execute_command(
            self._device.device_url,
            CMD_SET_EXPECTED_SHOWERS,
            [int_val],
        )
