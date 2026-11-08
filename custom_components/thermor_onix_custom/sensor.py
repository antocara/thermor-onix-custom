"""Sensor platform for the Thermor Onix DHW Plus integration."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Callable

from pyoverkiz.models import Device

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    EntityCategory,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolume,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    STATE_BOOSTER_HOURS,
    STATE_ENERGY_TOTAL,
    STATE_POWER_HEAT_ELECTRICAL,
    STATE_RSSI_LEVEL,
    STATE_SHOWERS_REMAINING,
    STATE_TARIFF_0,
    STATE_TARIFF_1,
    STATE_TARIFF_2,
    STATE_TEMP_INLET,
    STATE_TEMP_OUTLET,
    STATE_V40_VOLUME,
)
from .coordinator import ThermorDataUpdateCoordinator
from .entity import ThermorOnixEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ThermorSensorDescription(SensorEntityDescription):
    """Custom sensor entity description with state key and value transformer."""

    state_key: str = ""
    value_fn: Callable[[Any], Any] = lambda val: val


MAIN_DEVICE_SENSORS: tuple[ThermorSensorDescription, ...] = (
    ThermorSensorDescription(
        key="temp_outlet",
        name="Outlet Tank Temperature (Ready Water)",
        state_key=STATE_TEMP_OUTLET,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=lambda val: round(float(val), 1) if val is not None else None,
    ),
    ThermorSensorDescription(
        key="temp_inlet",
        name="Inlet Tank Temperature (Intermediate)",
        state_key=STATE_TEMP_INLET,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=lambda val: round(float(val), 1) if val is not None else None,
    ),
    ThermorSensorDescription(
        key="power_electric",
        name="Current Electrical Power",
        state_key=STATE_POWER_HEAT_ELECTRICAL,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda val: float(val) if val is not None else 0.0,
    ),
    ThermorSensorDescription(
        key="booster_operating_hours",
        name="Booster Operating Hours",
        state_key=STATE_BOOSTER_HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfTime.HOURS,
        icon="mdi:timer-outline",
        value_fn=lambda val: int(val) if val is not None else None,
    ),
    ThermorSensorDescription(
        key="v40_water_volume",
        name="Available Water Volume at 40°C",
        state_key=STATE_V40_VOLUME,
        device_class=SensorDeviceClass.VOLUME,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfVolume.LITERS,
        suggested_display_precision=1,
        icon="mdi:water-boiler",
        # Raw value is in ml (e.g. 61525 -> 61.5 L)
        value_fn=lambda val: round(float(val) / 1000.0, 1) if val is not None else None,
    ),
    ThermorSensorDescription(
        key="showers_remaining",
        name="Showers Available",
        state_key=STATE_SHOWERS_REMAINING,
        native_unit_of_measurement="showers",
        icon="mdi:shower-head",
        value_fn=lambda val: int(val) if val is not None else 0,
    ),
)

ENERGY_DEVICE_SENSORS: tuple[ThermorSensorDescription, ...] = (
    ThermorSensorDescription(
        key="energy_total",
        name="Total Electric Consumption",
        state_key=STATE_ENERGY_TOTAL,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
        value_fn=lambda val: round(float(val) / 1000.0, 2) if val is not None else None,
    ),
    ThermorSensorDescription(
        key="energy_tariff_0",
        name="Tariff 0 Consumption (Standard / Off-Peak)",
        state_key=STATE_TARIFF_0,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
        value_fn=lambda val: round(float(val) / 1000.0, 2) if val is not None else None,
    ),
    ThermorSensorDescription(
        key="energy_tariff_1",
        name="Tariff 1 Consumption (Morning / Showers)",
        state_key=STATE_TARIFF_1,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
        value_fn=lambda val: round(float(val) / 1000.0, 2) if val is not None else None,
    ),
    ThermorSensorDescription(
        key="energy_tariff_2",
        name="Tariff 2 Consumption (Boost Mode)",
        state_key=STATE_TARIFF_2,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
        value_fn=lambda val: round(float(val) / 1000.0, 2) if val is not None else None,
    ),
)

GATEWAY_DEVICE_SENSORS: tuple[ThermorSensorDescription, ...] = (
    ThermorSensorDescription(
        key="wifi_rssi",
        name="Wi-Fi Signal Strength",
        state_key=STATE_RSSI_LEVEL,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda val: int(val) if val is not None else None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities from a config entry."""
    coordinator: ThermorDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[ThermorSensor] = []

    # Sensors attached to the primary water heater
    if coordinator.main_device:
        for desc in MAIN_DEVICE_SENSORS:
            entities.append(ThermorSensor(coordinator, coordinator.main_device, desc))

    # Sensors attached to the energy consumption meter
    energy_dev = coordinator.energy_device or coordinator.main_device
    if energy_dev:
        for desc in ENERGY_DEVICE_SENSORS:
            entities.append(ThermorSensor(coordinator, energy_dev, desc))

    # Sensors attached to the gateway (Wi-Fi)
    gateway_dev = coordinator.gateway_device
    if gateway_dev:
        for desc in GATEWAY_DEVICE_SENSORS:
            entities.append(ThermorSensor(coordinator, gateway_dev, desc))

    async_add_entities(entities)


class ThermorSensor(ThermorOnixEntity, SensorEntity):
    """Representation of an individual Thermor Onix sensor."""

    entity_description: ThermorSensorDescription

    def __init__(
        self,
        coordinator: ThermorDataUpdateCoordinator,
        device: Device,
        description: ThermorSensorDescription,
    ) -> None:
        """Initialize the sensor entity."""
        super().__init__(coordinator, device, description.key)
        self.entity_description = description
        self._attr_name = description.name

    @property
    def native_value(self) -> Any:
        """Return the current sensor value processed through its transform function."""
        raw_val = self.get_state(self.entity_description.state_key)
        if raw_val is None:
            return None
        try:
            return self.entity_description.value_fn(raw_val)
        except (ValueError, TypeError) as err:
            _LOGGER.debug(
                "Error formatting raw value %s for sensor %s: %s",
                raw_val,
                self.entity_description.key,
                err,
            )
            return None
