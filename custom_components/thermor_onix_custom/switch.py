"""Switch platform for the Thermor Onix DHW Plus integration."""
from __future__ import annotations

import logging
from typing import Any

from pyoverkiz.models import Device

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CMD_SET_ABSENCE_MODE,
    CMD_SET_ANTI_LEGIONELLOSIS,
    CMD_SET_BOOST_MODE,
    CMD_SET_DHW_MODE,
    CMD_SET_SMART_GRID_OPTION,
    DOMAIN,
    STATE_ABSENCE_MODE,
    STATE_ANTI_LEGIONELLOSIS,
    STATE_BOOST_MODE,
    STATE_DHW_MODE,
    STATE_SMART_GRID,
)
from .coordinator import ThermorDataUpdateCoordinator
from .entity import ThermorOnixEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch entities from a config entry."""
    coordinator: ThermorDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    if coordinator.main_device:
        async_add_entities(
            [
                ThermorAntiLegionellaSwitch(coordinator, coordinator.main_device),
                ThermorSmartGridSwitch(coordinator, coordinator.main_device),
                ThermorBoostSwitch(coordinator, coordinator.main_device),
                ThermorAwaySwitch(coordinator, coordinator.main_device),
                ThermorEcoSwitch(coordinator, coordinator.main_device),
            ]
        )


class ThermorAntiLegionellaSwitch(ThermorOnixEntity, SwitchEntity):
    """Switch entity to enable or disable the periodic anti-legionella thermal disinfection cycle."""

    def __init__(
        self,
        coordinator: ThermorDataUpdateCoordinator,
        device: Device,
    ) -> None:
        """Initialize the anti-legionella switch."""
        super().__init__(coordinator, device, "anti_legionella")
        self._attr_name = "Anti-Legionella Cycle"
        self._attr_icon = "mdi:virus-off"

    @property
    def is_on(self) -> bool:
        """Return True if anti-legionella cycle is enabled."""
        val = self.get_state(STATE_ANTI_LEGIONELLOSIS)
        return str(val).lower() in ("1", "on", "true")

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on anti-legionella protection."""
        _LOGGER.info("Enabling anti-legionella protection on Thermor Onix")
        await self.coordinator.async_execute_command(
            self._device.device_url,
            CMD_SET_ANTI_LEGIONELLOSIS,
            [1],
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off anti-legionella protection."""
        _LOGGER.info("Disabling anti-legionella protection on Thermor Onix")
        await self.coordinator.async_execute_command(
            self._device.device_url,
            CMD_SET_ANTI_LEGIONELLOSIS,
            [0],
        )


class ThermorSmartGridSwitch(ThermorOnixEntity, SwitchEntity):
    """Switch entity to enable or disable the Smart Grid / solar surplus diversion input."""

    def __init__(
        self,
        coordinator: ThermorDataUpdateCoordinator,
        device: Device,
    ) -> None:
        """Initialize the Smart Grid switch."""
        super().__init__(coordinator, device, "smart_grid")
        self._attr_name = "Smart Grid / Solar Surplus Mode"
        self._attr_icon = "mdi:solar-power"

    @property
    def is_on(self) -> bool:
        """Return True if Smart Grid option is active."""
        val = self.get_state(STATE_SMART_GRID)
        return str(val).lower() == "active"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Activate Smart Grid mode."""
        _LOGGER.info("Activating Smart Grid mode on Thermor Onix")
        await self.coordinator.async_execute_command(
            self._device.device_url,
            CMD_SET_SMART_GRID_OPTION,
            ["active"],
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Deactivate Smart Grid mode."""
        _LOGGER.info("Deactivating Smart Grid mode on Thermor Onix")
        await self.coordinator.async_execute_command(
            self._device.device_url,
            CMD_SET_SMART_GRID_OPTION,
            ["deactive"],
        )


class ThermorBoostSwitch(ThermorOnixEntity, SwitchEntity):
    """Direct toggle switch to engage or cancel the rapid dual-tank Boost mode."""

    def __init__(
        self,
        coordinator: ThermorDataUpdateCoordinator,
        device: Device,
    ) -> None:
        """Initialize the boost switch."""
        super().__init__(coordinator, device, "boost_switch")
        self._attr_name = "Quick Boost"
        self._attr_icon = "mdi:rocket-launch"

    @property
    def is_on(self) -> bool:
        """Return True if Boost mode is currently active."""
        val = self.get_state(STATE_BOOST_MODE)
        return str(val).lower() == "on"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on Boost mode."""
        _LOGGER.info("Activating Boost mode on Thermor Onix")
        await self.coordinator.async_execute_command(
            self._device.device_url,
            CMD_SET_BOOST_MODE,
            ["on"],
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off Boost mode."""
        _LOGGER.info("Deactivating Boost mode on Thermor Onix")
        await self.coordinator.async_execute_command(
            self._device.device_url,
            CMD_SET_BOOST_MODE,
            ["off"],
        )


class ThermorAwaySwitch(ThermorOnixEntity, SwitchEntity):
    """Switch entity to toggle Away / Anti-frost mode (soft standby)."""

    def __init__(
        self,
        coordinator: ThermorDataUpdateCoordinator,
        device: Device,
    ) -> None:
        """Initialize the away switch."""
        super().__init__(coordinator, device, "away_switch")
        self._attr_name = "Away Mode (Anti-Frost)"
        self._attr_icon = "mdi:home-export-outline"

    @property
    def is_on(self) -> bool:
        """Return True if Away mode is currently active."""
        val = self.get_state(STATE_ABSENCE_MODE)
        return str(val).lower() == "on"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on Away mode."""
        _LOGGER.info("Activating Away mode on Thermor Onix")
        await self.coordinator.async_execute_command(
            self._device.device_url,
            CMD_SET_ABSENCE_MODE,
            ["on"],
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off Away mode."""
        _LOGGER.info("Deactivating Away mode on Thermor Onix")
        await self.coordinator.async_execute_command(
            self._device.device_url,
            CMD_SET_ABSENCE_MODE,
            ["off"],
        )


class ThermorEcoSwitch(ThermorOnixEntity, SwitchEntity):
    """Switch entity to toggle Eco power saving mode."""

    def __init__(
        self,
        coordinator: ThermorDataUpdateCoordinator,
        device: Device,
    ) -> None:
        """Initialize the eco switch."""
        super().__init__(coordinator, device, "eco_switch")
        self._attr_name = "Eco Mode"
        self._attr_icon = "mdi:leaf"

    @property
    def is_on(self) -> bool:
        """Return True if Eco mode is active."""
        val = self.get_state(STATE_DHW_MODE)
        return "ecoactive" in str(val).lower()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on Eco mode."""
        _LOGGER.info("Activating Eco mode on Thermor Onix")
        await self.coordinator.async_execute_command(
            self._device.device_url,
            CMD_SET_DHW_MODE,
            ["manualEcoActive"],
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off Eco mode (switch to manual)."""
        _LOGGER.info("Deactivating Eco mode on Thermor Onix")
        await self.coordinator.async_execute_command(
            self._device.device_url,
            CMD_SET_DHW_MODE,
            ["manualEcoInactive"],
        )
