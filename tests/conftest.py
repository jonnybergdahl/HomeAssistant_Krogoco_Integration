"""Fixtures for Krog & Co Calendar tests."""
from datetime import date, time
from unittest.mock import AsyncMock, Mock, patch

import pytest
from krog_company_ics import CalendarEvent
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import HomeAssistant

from custom_components.krog_company_calendar.const import CONF_BLACKLIST, CONF_CITY, CONF_MONTHS, DOMAIN

# This fixture is needed to allow pytest-homeassistant-custom-component to find the integration
pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield


@pytest.fixture
def mock_scraper():
    """Mock KrogocoIcs scraper."""
    with patch("custom_components.krog_company_calendar.coordinator.KrogocoIcs") as mock:
        yield mock


@pytest.fixture
def mock_calendar_events():
    """Return mock calendar events."""
    return [
        CalendarEvent(
            date=date(2026, 3, 15),
            title="Pianobar",
            url="https://krogoco.se/jonkoping/event/pianobar",
            all_day=False,
            start_time="18:00",
            end_time="22:00",
        ),
        CalendarEvent(
            date=date(2026, 3, 16),
            title="HV71 Match",
            url="https://krogoco.se/jonkoping/event/hv71",
            all_day=False,
            start_time="19:00",
            end_time="21:00",
        ),
        CalendarEvent(
            date=date(2026, 3, 17),
            title="All Day Festival",
            url="https://krogoco.se/jonkoping/event/festival",
            all_day=True,
        ),
        CalendarEvent(
            date=date(2026, 3, 18),
            title="Late Night Event",
            url="https://krogoco.se/jonkoping/event/latenight",
            all_day=False,
            start_time="23:00",
            end_time="02:00",  # Past midnight
        ),
    ]


@pytest.fixture
def mock_config_entry():
    """Return a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        entry_id="test_entry_id",
        data={
            CONF_CITY: "jonkoping",
            CONF_BLACKLIST: ["hv71"],
            CONF_MONTHS: 2,
        },
        options={},
    )


@pytest.fixture
async def mock_hass():
    """Return a mock Home Assistant instance."""
    hass = Mock(spec=HomeAssistant)
    hass.data = {DOMAIN: {}}
    hass.async_add_executor_job = AsyncMock()
    hass.config_entries = Mock()
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    hass.config_entries.async_reload = AsyncMock()
    return hass
