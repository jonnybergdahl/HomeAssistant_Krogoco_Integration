"""Config flow for Krog & Co Calendar integration."""
from __future__ import annotations

import logging
from typing import Any

from krog_company_ics import KrogocoIcs
import requests
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigEntry, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    CITIES,
    CONF_BLACKLIST,
    CONF_CITY,
    CONF_MONTHS,
    DEFAULT_MONTHS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class KrogCompanyCalendarConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Krog & Co Calendar."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            city = user_input[CONF_CITY]

            # Set unique_id based on city to prevent duplicates
            await self.async_set_unique_id(f"{DOMAIN}_{city}")
            self._abort_if_unique_id_configured()

            # Validate by attempting a test scrape
            url = f"https://krogoco.se/{city}/kalender/"
            blacklist_str = user_input.get(CONF_BLACKLIST, "")
            blacklist = [x.strip() for x in blacklist_str.split(",") if x.strip()]

            try:
                scraper = KrogocoIcs(url, DEFAULT_MONTHS, blacklist)
                await self.hass.async_add_executor_job(scraper.scrape_events)
            except requests.RequestException:
                _LOGGER.exception("Failed to connect to %s", url)
                errors["base"] = "cannot_connect"
            else:
                # Store blacklist as list
                return self.async_create_entry(
                    title=f"Krog & Co {CITIES[city]}",
                    data={
                        CONF_CITY: city,
                        CONF_BLACKLIST: blacklist,
                        CONF_MONTHS: DEFAULT_MONTHS,
                    },
                )

        # Build schema with city dropdown
        data_schema = vol.Schema(
            {
                vol.Required(CONF_CITY): vol.In(
                    {slug: name for slug, name in CITIES.items()}
                ),
                vol.Optional(CONF_BLACKLIST, default=""): cv.string,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return KrogCompanyCalendarOptionsFlow()


class KrogCompanyCalendarOptionsFlow(OptionsFlow):
    """Handle options flow for Krog & Co Calendar."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Convert blacklist string to list
            blacklist_str = user_input.get(CONF_BLACKLIST, "")
            blacklist = [x.strip() for x in blacklist_str.split(",") if x.strip()]

            # Update config entry data
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={
                    **self.config_entry.data,
                    CONF_BLACKLIST: blacklist,
                    CONF_MONTHS: user_input[CONF_MONTHS],
                },
            )
            return self.async_create_entry(title="", data={})

        # Get current values
        blacklist = self.config_entry.data.get(CONF_BLACKLIST, [])
        blacklist_str = ", ".join(blacklist) if blacklist else ""
        months = self.config_entry.data.get(CONF_MONTHS, DEFAULT_MONTHS)

        data_schema = vol.Schema(
            {
                vol.Optional(CONF_BLACKLIST, default=blacklist_str): cv.string,
                vol.Optional(CONF_MONTHS, default=months): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=12)
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
        )
