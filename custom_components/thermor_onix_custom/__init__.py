"""Initialization of the Thermor Onix DHW Plus integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from pyoverkiz.auth.credentials import UsernamePasswordCredentials
from pyoverkiz.client import OverkizClient
from pyoverkiz.enums import Server

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import (
    CONF_PASSWORD,
    CONF_POLL_INTERVAL,
    CONF_USERNAME,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import ThermorDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Thermor Onix DHW Plus from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    poll_interval = entry.options.get(
        CONF_POLL_INTERVAL,
        entry.data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL),
    )

    creds = UsernamePasswordCredentials(username=username, password=password)
    session = async_create_clientsession(hass)
    client = OverkizClient(
        server=Server.THERMOR_COZYTOUCH,
        credentials=creds,
        session=session,
    )

    coordinator = ThermorDataUpdateCoordinator(
        hass=hass,
        client=client,
        update_interval_sec=poll_interval,
    )

    # Perform initial refresh to verify connectivity and load devices
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        await client.close()
        raise

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward the entry setup to all supported platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Listen for configuration options changes (e.g. polling interval)
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry and clean up active sessions."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        coordinator: ThermorDataUpdateCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        # Close HTTP session if client provides a close method
        if hasattr(coordinator.client, "close"):
            await coordinator.client.close()

    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options dynamically when modified by user."""
    coordinator: ThermorDataUpdateCoordinator = hass.data[DOMAIN].get(entry.entry_id)
    if coordinator:
        new_interval = entry.options.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)
        coordinator.update_interval = timedelta(seconds=new_interval)
        _LOGGER.info("Thermor Onix polling interval updated to %s seconds", new_interval)
