"""Water Heater platform for the Thermor Onix DHW Plus integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.water_heater import (
    STATE_ECO,
    STATE_ELECTRIC,
    STATE_OFF,
    STATE_PERFORMANCE,
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CMD_SET_ABSENCE_MODE,
    CMD_SET_BOOST_MODE,
    CMD_SET_DHW_MODE,
    CMD_SET_EXPECTED_SHOWERS,
    DOMAIN,
    STATE_ABSENCE_MODE,
    STATE_BOOSTER_HOURS,
    STATE_BOOST_MODE,
    STATE_DHW_MODE,
    STATE_HEATING_STATUS,
    STATE_SHOWERS_REMAINING,
    STATE_TEMP_INLET,
    STATE_TEMP_OUTLET,
    STATE_V40_VOLUME,
    STATE_WATER_TARGET_TEMP,
)
from .coordinator import ThermorDataUpdateCoordinator
from .entity import ThermorOnixEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the water heater entity from a config entry."""
    coordinator: ThermorDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    if coordinator.main_device:
        async_add_entities(
            [ThermorOnixWaterHeater(coordinator, coordinator.main_device)]
        )


class ThermorOnixWaterHeater(ThermorOnixEntity, WaterHeaterEntity):
    """Primary domestic hot water entity for Thermor Onix double-tank heaters."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        WaterHeaterEntityFeature.TARGET_TEMPERATURE
        | WaterHeaterEntityFeature.OPERATION_MODE
    )
    _attr_operation_list = [
        STATE_ELECTRIC,     # Standard manual mode
        STATE_ECO,          # Eco mode
        STATE_PERFORMANCE,  # Boost / rapid heating mode
        STATE_OFF,          # Away / frost protection mode
    ]
    _attr_min_temp = 50.0
    _attr_max_temp = 70.0
    _attr_target_temperature_step = 1.0

    def __init__(
        self,
        coordinator: ThermorDataUpdateCoordinator,
        device: Any,
    ) -> None:
        """Initialize the water heater entity."""
        super().__init__(coordinator, device, "water_heater")
        self._attr_name = "Water Heater"

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature measured in the outlet tank (ready water)."""
        temp = self.get_state(STATE_TEMP_OUTLET)
        if temp is not None:
            try:
                return float(temp)
            except (ValueError, TypeError):
                pass
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the target hot water temperature setpoint."""
        target = self.get_state(STATE_WATER_TARGET_TEMP)
        if target is not None:
            try:
                return float(target)
            except (ValueError, TypeError):
                pass
        return 50.0

    @property
    def current_operation(self) -> str:
        """Calculate the current operation mode based on device states."""
        absence = str(self.get_state(STATE_ABSENCE_MODE, "off")).lower()
        if absence == "on":
            return STATE_OFF

        boost = str(self.get_state(STATE_BOOST_MODE, "off")).lower()
        if boost == "on":
            return STATE_PERFORMANCE

        dhw_mode = str(self.get_state(STATE_DHW_MODE, "manualEcoInactive")).lower()
        if dhw_mode in ("automode", "auto", "manualecoactive", "eco"):
            return STATE_ECO

        return STATE_ELECTRIC

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extended telemetry attributes for dual tanks and internal state."""
        attrs: dict[str, Any] = {}

        temp_outlet = self.get_state(STATE_TEMP_OUTLET)
        if temp_outlet is not None:
            attrs["outlet_tank_temperature_c"] = float(temp_outlet)

        temp_inlet = self.get_state(STATE_TEMP_INLET)
        if temp_inlet is not None:
            attrs["inlet_tank_temperature_c"] = float(temp_inlet)

        booster_hours = self.get_state(STATE_BOOSTER_HOURS)
        if booster_hours is not None:
            attrs["booster_lifetime_operating_hours"] = booster_hours

        v40 = self.get_state(STATE_V40_VOLUME)
        if v40 is not None:
            try:
                attrs["v40_water_volume_liters"] = round(float(v40) / 1000.0, 1)
            except (ValueError, TypeError):
                pass

        showers = self.get_state(STATE_SHOWERS_REMAINING)
        if showers is not None:
            attrs["showers_remaining"] = showers

        heating = self.get_state(STATE_HEATING_STATUS)
        attrs["is_heating"] = (str(heating).lower() == "on")

        return attrs

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target hot water temperature."""
        target_temp = kwargs.get(ATTR_TEMPERATURE)
        if target_temp is None:
            return

        target_temp = max(self._attr_min_temp, min(self._attr_max_temp, float(target_temp)))
        # Thermor Onix double-tank hardware regulates temperature via shower capacity (1 to 5 showers)
        # 50°C -> 1 shower, 55°C -> 2 showers, 60°C -> 3 showers, 65°C -> 4 showers, 70°C -> 5 showers
        target_showers = int(round((target_temp - 50.0) / 5.0)) + 1
        target_showers = max(1, min(5, target_showers))
        _LOGGER.info(
            "Setting Thermor Onix target temperature to %.1f °C (mapped to %d showers)",
            target_temp,
            target_showers,
        )

        await self.coordinator.async_execute_command(
            self._device.device_url,
            CMD_SET_EXPECTED_SHOWERS,
            [target_showers],
        )

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set operation mode (electric, eco, performance, off)."""
        _LOGGER.info("Setting Thermor Onix operation mode to: %s", operation_mode)

        if operation_mode == STATE_PERFORMANCE:
            # Rapid Boost mode
            await self.coordinator.async_execute_command(
                self._device.device_url,
                CMD_SET_BOOST_MODE,
                ["on"],
            )
        elif operation_mode == STATE_OFF:
            # Away / frost protection mode
            await self.coordinator.async_execute_command(
                self._device.device_url,
                CMD_SET_ABSENCE_MODE,
                ["on"],
            )
        elif operation_mode == STATE_ECO:
            # Deactivate away mode if active
            if str(self.get_state(STATE_ABSENCE_MODE)).lower() == "on":
                await self.coordinator.async_execute_command(
                    self._device.device_url, CMD_SET_ABSENCE_MODE, ["off"]
                )
            if str(self.get_state(STATE_BOOST_MODE)).lower() == "on":
                await self.coordinator.async_execute_command(
                    self._device.device_url, CMD_SET_BOOST_MODE, ["off"]
                )
            await self.coordinator.async_execute_command(
                self._device.device_url,
                CMD_SET_DHW_MODE,
                ["autoMode"],
            )
        elif operation_mode == STATE_ELECTRIC:
            # Standard manual mode
            if str(self.get_state(STATE_ABSENCE_MODE)).lower() == "on":
                await self.coordinator.async_execute_command(
                    self._device.device_url, CMD_SET_ABSENCE_MODE, ["off"]
                )
            if str(self.get_state(STATE_BOOST_MODE)).lower() == "on":
                await self.coordinator.async_execute_command(
                    self._device.device_url, CMD_SET_BOOST_MODE, ["off"]
                )
            await self.coordinator.async_execute_command(
                self._device.device_url,
                CMD_SET_DHW_MODE,
                ["manualEcoInactive"],
            )
