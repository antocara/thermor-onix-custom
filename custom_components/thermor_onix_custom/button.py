"""Button platform for the Thermor Onix DHW Plus integration."""
from __future__ import annotations

import logging

from pyoverkiz.models import Device

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.util.dt as dt_util

from .const import CMD_SET_DATE_TIME, DOMAIN
from .coordinator import ThermorDataUpdateCoordinator
from .entity import ThermorOnixEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button entities from a config entry."""
    coordinator: ThermorDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    if coordinator.main_device:
        async_add_entities(
            [
                ThermorSyncClockButton(coordinator, coordinator.main_device),
                ThermorRefreshButton(coordinator, coordinator.main_device),
            ]
        )


class ThermorSyncClockButton(ThermorOnixEntity, ButtonEntity):
    """Button to synchronize the water heater internal clock with Home Assistant time."""

    def __init__(
        self,
        coordinator: ThermorDataUpdateCoordinator,
        device: Device,
    ) -> None:
        """Initialize the sync clock button."""
        super().__init__(coordinator, device, "sync_clock")
        self._attr_name = "Synchronize Internal Clock"
        self._attr_icon = "mdi:clock-sync"

    async def async_press(self) -> None:
        """Send current local date and time to the water heater."""
        now = dt_util.now()
        # Cozytouch Overkiz driver expects weekday in range 0-6 (0=Sunday, 1=Monday, ..., 6=Saturday)
        overkiz_weekday = (now.weekday() + 1) % 7
        date_time_payload = {
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "weekday": overkiz_weekday,
            "hour": now.hour,
            "minute": now.minute,
            "second": now.second,
        }

        _LOGGER.info(
            "Synchronizing Thermor Onix internal clock with local time: %s",
            date_time_payload,
        )

        await self.coordinator.async_execute_command(
            self._device.device_url,
            CMD_SET_DATE_TIME,
            [date_time_payload],
        )


class ThermorRefreshButton(ThermorOnixEntity, ButtonEntity):
    """Button to force an immediate telemetry refresh from the Overkiz cloud."""

    def __init__(
        self,
        coordinator: ThermorDataUpdateCoordinator,
        device: Device,
    ) -> None:
        """Initialize the refresh button."""
        super().__init__(coordinator, device, "refresh_telemetry")
        self._attr_name = "Refresh Telemetry Now"
        self._attr_icon = "mdi:refresh"

    async def async_press(self) -> None:
        """Trigger an immediate data coordinator refresh."""
        _LOGGER.info("Manually triggering telemetry refresh for Thermor Onix")
        await self.coordinator.async_request_refresh()
