"""Test the Krog & Co Calendar init."""
from unittest.mock import patch

import pytest

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from custom_components.krog_company_calendar import (
    async_reload_entry,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.krog_company_calendar.const import (
    CONF_BLACKLIST,
    CONF_CITY,
    CONF_MONTHS,
    DOMAIN,
)


async def test_async_setup_entry(
    hass: HomeAssistant, mock_config_entry, mock_scraper, mock_calendar_events
) -> None:
    """Test setting up the integration."""
    mock_scraper.return_value.scrape_events.return_value = mock_calendar_events
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.krog_company_calendar.coordinator.KrogocoIcs",
        return_value=mock_scraper.return_value,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert DOMAIN in hass.data
    assert mock_config_entry.entry_id in hass.data[DOMAIN]

    # Verify coordinator was created with correct params
    coordinator = hass.data[DOMAIN][mock_config_entry.entry_id]
    assert coordinator.city == "jonkoping"
    assert coordinator.months == 2
    assert coordinator.blacklist == ["hv71"]


async def test_async_unload_entry(hass: HomeAssistant, mock_config_entry) -> None:
    """Test unloading the integration."""
    from unittest.mock import Mock

    # Set up initial data
    hass.data[DOMAIN] = {mock_config_entry.entry_id: Mock()}

    result = await async_unload_entry(hass, mock_config_entry)

    assert result is True
    assert mock_config_entry.entry_id not in hass.data[DOMAIN]


async def test_async_unload_entry_failure(hass: HomeAssistant, mock_config_entry) -> None:
    """Test unloading the integration fails."""
    from unittest.mock import Mock

    # Set up initial data
    hass.data[DOMAIN] = {mock_config_entry.entry_id: Mock()}

    # Make unload fail by mocking the platform unload
    with patch(
        "homeassistant.config_entries.ConfigEntries.async_unload_platforms",
        return_value=False,
    ):
        result = await async_unload_entry(hass, mock_config_entry)

    assert result is False
    # Data should not be removed if unload failed
    assert mock_config_entry.entry_id in hass.data[DOMAIN]


async def test_async_reload_entry(hass: HomeAssistant, mock_config_entry) -> None:
    """Test reloading the integration."""
    with patch("homeassistant.config_entries.ConfigEntries.async_reload") as mock_reload:
        await async_reload_entry(hass, mock_config_entry)
        mock_reload.assert_called_once_with(mock_config_entry.entry_id)


async def test_setup_entry_default_values(
    hass: HomeAssistant, mock_scraper, mock_calendar_events
) -> None:
    """Test setup with default values for optional config."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        entry_id="test_entry_id_2",
        data={
            CONF_CITY: "gavle",
            # No CONF_BLACKLIST or CONF_MONTHS - should use defaults
        },
    )
    config_entry.add_to_hass(hass)

    mock_scraper.return_value.scrape_events.return_value = mock_calendar_events

    with patch(
        "custom_components.krog_company_calendar.coordinator.KrogocoIcs",
        return_value=mock_scraper.return_value,
    ):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    assert coordinator.city == "gavle"
    assert coordinator.months == 2  # DEFAULT_MONTHS
    assert coordinator.blacklist == []  # Default empty list
