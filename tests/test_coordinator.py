"""Test the Krog & Co Calendar coordinator."""
from datetime import timedelta
from unittest.mock import patch

import pytest
import requests

from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.util import dt as dt_util

from custom_components.krog_company_calendar.coordinator import (
    KrogCompanyCalendarCoordinator,
)


async def test_coordinator_update_success(
    mock_hass, mock_config_entry, mock_scraper, mock_calendar_events
) -> None:
    """Test successful coordinator update."""
    mock_scraper.return_value.scrape_events.return_value = mock_calendar_events
    mock_hass.async_add_executor_job.return_value = mock_calendar_events

    coordinator = KrogCompanyCalendarCoordinator(
        mock_hass,
        mock_config_entry,
        city="jonkoping",
        months=2,
        blacklist=["hv71"],
    )

    with patch(
        "custom_components.krog_company_calendar.coordinator.KrogocoIcs",
        return_value=mock_scraper.return_value,
    ):
        result = await coordinator._async_update_data()

    assert result == mock_calendar_events
    assert coordinator.url == "https://krogoco.se/jonkoping/kalender/"
    assert coordinator.city == "jonkoping"
    assert coordinator.months == 2
    assert coordinator.blacklist == ["hv71"]


async def test_coordinator_update_failure(mock_hass, mock_config_entry, mock_scraper) -> None:
    """Test coordinator update failure."""
    mock_scraper.return_value.scrape_events.side_effect = requests.RequestException(
        "Connection failed"
    )
    mock_hass.async_add_executor_job.side_effect = requests.RequestException(
        "Connection failed"
    )

    coordinator = KrogCompanyCalendarCoordinator(
        mock_hass,
        mock_config_entry,
        city="jonkoping",
        months=2,
        blacklist=[],
    )

    with patch(
        "custom_components.krog_company_calendar.coordinator.KrogocoIcs",
        return_value=mock_scraper.return_value,
    ):
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()


async def test_coordinator_update_interval(mock_hass, mock_config_entry) -> None:
    """Test coordinator has correct update interval."""
    coordinator = KrogCompanyCalendarCoordinator(
        mock_hass,
        mock_config_entry,
        city="jonkoping",
        months=2,
        blacklist=[],
    )

    assert coordinator.update_interval == timedelta(minutes=180)


async def test_coordinator_different_cities(
    mock_hass, mock_config_entry, mock_scraper, mock_calendar_events
) -> None:
    """Test coordinator works with different cities."""
    cities = ["gavle", "halmstad", "ljungby", "varnamo"]

    for city in cities:
        coordinator = KrogCompanyCalendarCoordinator(
            mock_hass,
            mock_config_entry,
            city=city,
            months=2,
            blacklist=[],
        )
        assert coordinator.url == f"https://krogoco.se/{city}/kalender/"
