"""Time platform for the Thermor Onix DHW Plus integration."""
from __future__ import annotations

from datetime import time
import logging
from typing import Any

from pyoverkiz.models import Device

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CMD_SET_PROGRAMMING_SLOTS,
    DOMAIN,
    STATE_PROGRAMMING_SLOTS,
)
from .coordinator import ThermorDataUpdateCoordinator
from .entity import ThermorOnixEntity

_LOGGER = logging.getLogger(__name__)

SLOT_DEFINITIONS = (
    ("slot1", "start", "Slot 1 Start Time", "mdi:clock-start"),
    ("slot1", "end", "Slot 1 End Time", "mdi:clock-end"),
    ("slot2", "start", "Slot 2 Start Time", "mdi:clock-start"),
    ("slot2", "end", "Slot 2 End Time", "mdi:clock-end"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up time entities from a config entry."""
    coordinator: ThermorDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    if coordinator.main_device:
        entities = [
            ThermorProgrammingSlotTime(
                coordinator,
                coordinator.main_device,
                slot_name,
                field,
                name,
                icon,
            )
            for slot_name, field, name, icon in SLOT_DEFINITIONS
        ]
        async_add_entities(entities)


class ThermorProgrammingSlotTime(ThermorOnixEntity, TimeEntity):
    """Time entity to configure hardware programming slot times."""

    def __init__(
        self,
        coordinator: ThermorDataUpdateCoordinator,
        device: Device,
        slot_name: str,
        field: str,
        name: str,
        icon: str,
    ) -> None:
        """Initialize the time entity."""
        key = f"{slot_name}_{field}"
        super().__init__(coordinator, device, key)
        self._slot_name = slot_name
        self._field = field
        self._attr_name = name
        self._attr_icon = icon

    @property
    def native_value(self) -> time | None:
        """Return the current time configured in this slot."""
        slots = self.get_state(STATE_PROGRAMMING_SLOTS)
        if not isinstance(slots, dict):
            return time(0, 0)

        slot_data = slots.get(self._slot_name, {})
        time_str = slot_data.get(self._field, "00:00")
        try:
            parts = str(time_str).split(":")
            return time(int(parts[0]), int(parts[1]))
        except (ValueError, IndexError):
            return time(0, 0)

    async def async_set_value(self, value: time) -> None:
        """Send updated programming slot configuration to the water heater."""
        slots = self.get_state(STATE_PROGRAMMING_SLOTS)
        if not isinstance(slots, dict):
            slots = {
                "slot1": {"start": "07:30", "end": "08:00"},
                "slot2": {"start": "00:00", "end": "00:00"},
            }
        else:
            # Create a shallow copy to prevent mutation issues
            slots = {
                "slot1": dict(slots.get("slot1", {"start": "00:00", "end": "00:00"})),
                "slot2": dict(slots.get("slot2", {"start": "00:00", "end": "00:00"})),
            }

        new_time_str = value.strftime("%H:%M")
        slots[self._slot_name][self._field] = new_time_str

        _LOGGER.info(
            "Setting Thermor Onix %s %s to %s (Full payload: %s)",
            self._slot_name,
            self._field,
            new_time_str,
            slots,
        )

        await self.coordinator.async_execute_command(
            self._device.device_url,
            CMD_SET_PROGRAMMING_SLOTS,
            [slots],
        )
