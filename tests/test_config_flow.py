"""Test the Krog & Co Calendar config flow."""
from unittest.mock import patch

import pytest
import requests

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.krog_company_calendar.const import (
    CONF_BLACKLIST,
    CONF_CITY,
    CONF_MONTHS,
    DEFAULT_MONTHS,
    DOMAIN,
)


async def test_form(hass: HomeAssistant, mock_scraper, mock_calendar_events) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    # Mock successful scrape
    mock_scraper.return_value.scrape_events.return_value = mock_calendar_events

    with patch(
        "custom_components.krog_company_calendar.config_flow.KrogocoIcs",
        return_value=mock_scraper.return_value,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_CITY: "jonkoping",
                CONF_BLACKLIST: "hv71, matchb",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Krog & Co Jönköping"
    assert result2["data"] == {
        CONF_CITY: "jonkoping",
        CONF_BLACKLIST: ["hv71", "matchb"],
        CONF_MONTHS: DEFAULT_MONTHS,
    }


async def test_form_cannot_connect(hass: HomeAssistant, mock_scraper) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Mock connection error
    mock_scraper.return_value.scrape_events.side_effect = requests.RequestException

    with patch(
        "custom_components.krog_company_calendar.config_flow.KrogocoIcs",
        return_value=mock_scraper.return_value,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_CITY: "jonkoping",
                CONF_BLACKLIST: "",
            },
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_form_already_configured(hass: HomeAssistant, mock_scraper, mock_calendar_events, mock_config_entry) -> None:
    """Test we handle already configured."""
    # Create existing entry
    mock_config_entry.add_to_hass(hass)

    # Set unique_id for the entry
    hass.config_entries.async_update_entry(
        mock_config_entry, unique_id=f"{DOMAIN}_jonkoping"
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    mock_scraper.return_value.scrape_events.return_value = mock_calendar_events

    with patch(
        "custom_components.krog_company_calendar.config_flow.KrogocoIcs",
        return_value=mock_scraper.return_value,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_CITY: "jonkoping",
                CONF_BLACKLIST: "",
            },
        )

    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "already_configured"


async def test_options_flow(hass: HomeAssistant, mock_config_entry) -> None:
    """Test options flow."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_BLACKLIST: "new, blacklist",
            CONF_MONTHS: 3,
        },
    )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert mock_config_entry.options[CONF_BLACKLIST] == ["new", "blacklist"]
    assert mock_config_entry.options[CONF_MONTHS] == 3


async def test_options_flow_empty_blacklist(hass: HomeAssistant, mock_config_entry) -> None:
    """Test options flow with empty blacklist."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_BLACKLIST: "",
            CONF_MONTHS: 2,
        },
    )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert mock_config_entry.options[CONF_BLACKLIST] == []
    assert mock_config_entry.options[CONF_MONTHS] == 2
