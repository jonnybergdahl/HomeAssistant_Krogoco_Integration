"""The Krog & Co Calendar integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_BLACKLIST, CONF_CITY, CONF_MONTHS, DEFAULT_MONTHS, DOMAIN
from .coordinator import KrogCompanyCalendarCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.CALENDAR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Krog & Co Calendar from a config entry."""
    city = entry.data[CONF_CITY]
    # Options take precedence over data for reconfigurable values
    blacklist = entry.options.get(CONF_BLACKLIST, entry.data.get(CONF_BLACKLIST, []))
    months = int(entry.options.get(CONF_MONTHS, entry.data.get(CONF_MONTHS, DEFAULT_MONTHS)))

    coordinator = KrogCompanyCalendarCoordinator(hass, entry, city, months, blacklist)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register options flow update listener
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)
