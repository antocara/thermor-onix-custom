"""Binary Sensor platform for the Thermor Onix DHW Plus integration."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Callable

from pyoverkiz.models import Device

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    STATE_ABSENCE_MODE,
    STATE_BOOST_MODE,
    STATE_DHW_ERROR,
    STATE_HEATING_STATUS,
)
from .coordinator import ThermorDataUpdateCoordinator
from .entity import ThermorOnixEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ThermorBinarySensorDescription(BinarySensorEntityDescription):
    """Custom binary sensor description with a boolean evaluation function."""

    state_key: str = ""
    is_on_fn: Callable[[Any], bool] = lambda val: bool(val)


def _check_error_state(val: Any) -> bool:
    """Evaluate if the error state reports an active fault (255 = no error in Atlantic modbuslink)."""
    if val is None:
        return False
    if isinstance(val, dict):
        code = val.get("code")
        # 255 indicates normal operation / no faults in Atlantic/Thermor modbuslink protocol
        return code is not None and code not in (0, 255)
    return False


BINARY_SENSORS: tuple[ThermorBinarySensorDescription, ...] = (
    ThermorBinarySensorDescription(
        key="heating_active",
        name="Heating Active",
        state_key=STATE_HEATING_STATUS,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:fire",
        is_on_fn=lambda val: str(val).lower() == "on",
    ),
    ThermorBinarySensorDescription(
        key="boost_active",
        name="Boost Mode Active",
        state_key=STATE_BOOST_MODE,
        icon="mdi:rocket-launch",
        is_on_fn=lambda val: str(val).lower() == "on",
    ),
    ThermorBinarySensorDescription(
        key="absence_active",
        name="Away Mode Active",
        state_key=STATE_ABSENCE_MODE,
        icon="mdi:home-export-outline",
        is_on_fn=lambda val: str(val).lower() == "on",
    ),
    ThermorBinarySensorDescription(
        key="dhw_error",
        name="Hardware Fault or Alert",
        state_key=STATE_DHW_ERROR,
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=_check_error_state,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor entities from a config entry."""
    coordinator: ThermorDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    if coordinator.main_device:
        entities = [
            ThermorBinarySensor(coordinator, coordinator.main_device, desc)
            for desc in BINARY_SENSORS
        ]
        async_add_entities(entities)


class ThermorBinarySensor(ThermorOnixEntity, BinarySensorEntity):
    """Representation of an individual Thermor Onix binary sensor."""

    entity_description: ThermorBinarySensorDescription

    def __init__(
        self,
        coordinator: ThermorDataUpdateCoordinator,
        device: Device,
        description: ThermorBinarySensorDescription,
    ) -> None:
        """Initialize the binary sensor entity."""
        super().__init__(coordinator, device, description.key)
        self.entity_description = description
        self._attr_name = description.name

    @property
    def is_on(self) -> bool:
        """Return True if the binary state is active."""
        raw_val = self.get_state(self.entity_description.state_key)
        try:
            return self.entity_description.is_on_fn(raw_val)
        except Exception:
            return False
