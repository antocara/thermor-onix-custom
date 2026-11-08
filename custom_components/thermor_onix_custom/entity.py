"""Base entity for the Thermor Onix DHW Plus integration."""
from __future__ import annotations

from typing import Any

from pyoverkiz.models import Device

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ThermorDataUpdateCoordinator


class ThermorOnixEntity(CoordinatorEntity[ThermorDataUpdateCoordinator]):
    """Base class for all entities belonging to a Thermor Onix water heater."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ThermorDataUpdateCoordinator,
        device: Device,
        key: str,
    ) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self._device = device
        self._key = key
        self._attr_unique_id = f"{device.device_url}_{key}"

    @property
    def device(self) -> Device:
        """Return the latest fresh device instance from coordinator data."""
        if self.coordinator.data and "devices" in self.coordinator.data:
            return self.coordinator.data["devices"].get(self._device.device_url, self._device)
        return self._device

    @property
    def device_info(self) -> DeviceInfo:
        """Return device registry information to group all entities under one device card."""
        main_dev = self.coordinator.main_device or self.device
        model_name = "Onix 80L (Double Tank)"
        manufacturer = "Thermor (Atlantic Group)"

        # Extract capacity and model name if present in device states
        capacity = self.get_state_from_device(main_dev, "modbuslink:DHWCapacityState")
        if capacity:
            model_name = f"Onix {capacity}L (Double Tank)"

        return DeviceInfo(
            identifiers={(DOMAIN, main_dev.device_url)},
            name="Thermor Onix",
            manufacturer=manufacturer,
            model=model_name,
            suggested_area="Bathroom",
        )

    def get_state(self, state_name: str, default: Any = None) -> Any:
        """Return the latest value of a state from this entity's device."""
        return self.get_state_from_device(self.device, state_name, default)

    @staticmethod
    def get_state_from_device(device: Device | None, state_name: str, default: Any = None) -> Any:
        """Safely extract the value of a state from an Overkiz Device object."""
        if not device or not device.states:
            return default

        # In pyoverkiz, device.states can be a dictionary or list
        state_obj = None
        if hasattr(device.states, "get"):
            state_obj = device.states.get(state_name)
        elif isinstance(device.states, list):
            for s in device.states:
                if getattr(s, "name", None) == state_name:
                    state_obj = s
                    break

        if state_obj is None:
            return default

        return getattr(state_obj, "value", state_obj)
