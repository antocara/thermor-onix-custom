"""DataUpdateCoordinator for the Thermor Onix DHW Plus integration."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

from pyoverkiz.client import OverkizClient
from pyoverkiz.exceptions import (
    BadCredentialsError,
    MaintenanceError,
    OverkizError,
    TooManyRequestsError,
)
from pyoverkiz.models import Action, Command, Device

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ThermorDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator responsible for polling and managing communication with the Cozytouch / Overkiz API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: OverkizClient,
        update_interval_sec: int = 60,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_coordinator",
            update_interval=timedelta(seconds=update_interval_sec),
        )
        self.client = client
        self.main_device: Device | None = None
        self.energy_device: Device | None = None
        self.gateway_device: Device | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch all device states from the Overkiz cloud."""
        try:
            setup = await self.client.get_setup()
            devices_by_url: dict[str, Device] = {}

            for device in setup.devices:
                devices_by_url[device.device_url] = device

                # Identify primary domestic hot water production device
                if device.widget == "DomesticHotWaterProduction" or device.device_url.endswith("1#1"):
                    self.main_device = device
                # Identify cumulative electric energy sensor device
                elif (
                    device.widget == "CumulativeElectricPowerConsumptionSensor"
                    or device.device_url.endswith("1#2")
                ):
                    self.energy_device = device
                # Identify internal uPod gateway
                elif "uPod" in device.device_url or device.widget == "Pod":
                    self.gateway_device = device

            if not self.main_device:
                raise UpdateFailed("No domestic hot water device found in Thermor account.")

            return {
                "devices": devices_by_url,
                "main_device": self.main_device,
                "energy_device": self.energy_device,
                "gateway_device": self.gateway_device,
            }

        except BadCredentialsError as err:
            raise ConfigEntryAuthFailed("Invalid Thermor Cozytouch credentials.") from err
        except TooManyRequestsError as err:
            _LOGGER.warning("Overkiz rate limit reached, waiting for next cycle: %s", err)
            raise UpdateFailed(f"Rate limit on Overkiz cloud: {err}") from err
        except MaintenanceError as err:
            _LOGGER.warning("Cozytouch server temporarily undergoing maintenance: %s", err)
            raise UpdateFailed(f"Cozytouch server maintenance: {err}") from err
        except OverkizError as err:
            raise UpdateFailed(f"Communication error with Overkiz: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error while fetching data: {err}") from err

    async def async_execute_command(
        self,
        device_url: str,
        command_name: str,
        parameters: list[Any] | None = None,
    ) -> str | None:
        """Send a command to the device and trigger a state refresh."""
        parameters = parameters or []
        _LOGGER.debug(
            "Sending command to %s: %s with parameters %s",
            device_url,
            command_name,
            parameters,
        )

        try:
            cmd = Command(name=command_name, parameters=parameters)
            action = Action(device_url=device_url, commands=[cmd])
            exec_id = await self.client.execute_action_group(
                actions=[action],
                label=f"HA: {command_name}",
            )
            _LOGGER.info(
                "Command %s executed successfully on Thermor Onix (Action ID: %s)",
                command_name,
                exec_id,
            )

            # Short delay to allow the cloud to propagate the hardware state change
            await asyncio.sleep(1.5)
            await self.async_request_refresh()
            return exec_id

        except OverkizError as err:
            _LOGGER.error("Failed to execute command %s: %s", command_name, err)
            raise
