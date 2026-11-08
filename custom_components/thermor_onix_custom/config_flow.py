"""Config Flow for the Thermor Onix DHW Plus integration."""
from __future__ import annotations

import logging
from typing import Any

from pyoverkiz.auth.credentials import UsernamePasswordCredentials
from pyoverkiz.client import OverkizClient
from pyoverkiz.enums import Server
from pyoverkiz.exceptions import (
    BadCredentialsError,
    MaintenanceError,
    OverkizError,
    TooManyRequestsError,
)
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_PASSWORD,
    CONF_POLL_INTERVAL,
    CONF_SERVER,
    CONF_USERNAME,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_SERVER,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=30, max=600)
        ),
    }
)


async def validate_credentials(user_input: dict[str, Any]) -> dict[str, Any]:
    """Validate credentials by connecting directly to the Overkiz API."""
    username = user_input[CONF_USERNAME]
    password = user_input[CONF_PASSWORD]

    creds = UsernamePasswordCredentials(username=username, password=password)
    async with OverkizClient(server=Server.THERMOR_COZYTOUCH, credentials=creds) as client:
        await client.login()
        setup = await client.get_setup()
        gateway_id = setup.gateways[0].gateway_id if setup.gateways else username
        return {"gateway_id": gateway_id, "title": f"Thermor Onix ({username})"}


class ThermorOnixConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Thermor Onix DHW Plus."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle initial step when user adds the integration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_credentials(user_input)

                # Avoid configuring the same account multiple times
                await self.async_set_unique_id(user_input[CONF_USERNAME].lower())
                self._abort_if_unique_id_configured()

                user_input[CONF_SERVER] = DEFAULT_SERVER
                return self.async_create_entry(title=info["title"], data=user_input)

            except BadCredentialsError:
                errors["base"] = "invalid_auth"
            except TooManyRequestsError:
                errors["base"] = "too_many_requests"
            except MaintenanceError:
                errors["base"] = "server_maintenance"
            except OverkizError as err:
                _LOGGER.error("Failed to connect to Thermor API: %s", err)
                errors["base"] = "cannot_connect"
            except Exception as err:
                _LOGGER.exception("Unexpected error in config flow: %s", err)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=USER_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Return the options flow handler to allow changing settings dynamically."""
        return ThermorOnixOptionsFlowHandler(config_entry)


class ThermorOnixOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options updates (such as polling interval)."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options handler."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage options form."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_POLL_INTERVAL,
            self.config_entry.data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL),
        )

        options_schema = vol.Schema(
            {
                vol.Required(CONF_POLL_INTERVAL, default=current_interval): vol.All(
                    vol.Coerce(int), vol.Range(min=30, max=600)
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)
