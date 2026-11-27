"""Test the Krog & Co Calendar entity."""
from datetime import date, datetime, time, timedelta
from unittest.mock import Mock

import pytest
from freezegun import freeze_time

from homeassistant.components.calendar import CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.krog_company_calendar.calendar import KrogCompanyCalendar
from custom_components.krog_company_calendar.const import DOMAIN


@pytest.fixture
def mock_coordinator(mock_hass, mock_calendar_events):
    """Return a mock coordinator."""
    coordinator = Mock()
    coordinator.data = mock_calendar_events
    coordinator.city = "jonkoping"
    coordinator.hass = mock_hass
    return coordinator


@pytest.fixture
def calendar_entity(mock_coordinator, mock_config_entry):
    """Return a calendar entity."""
    return KrogCompanyCalendar(mock_coordinator, mock_config_entry)


async def test_calendar_entity_attributes(calendar_entity) -> None:
    """Test calendar entity attributes."""
    assert calendar_entity._attr_name == "Jönköping"
    assert calendar_entity._attr_unique_id == f"{DOMAIN}_jonkoping"
    assert calendar_entity._attr_has_entity_name is True
    assert calendar_entity._attr_device_info["name"] == "Krog & Co Jönköping"
    assert calendar_entity._attr_device_info["manufacturer"] == "Krog & Co"


@freeze_time("2026-03-14 12:00:00")
async def test_calendar_event_property_next_event(calendar_entity) -> None:
    """Test event property returns next event."""
    event = calendar_entity.event

    assert event is not None
    assert event.summary == "Pianobar"
    assert event.start == datetime(2026, 3, 15, 18, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)
    assert event.end == datetime(2026, 3, 15, 22, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)
    assert event.description == "https://krogoco.se/jonkoping/event/pianobar"


# Tests run with US/Pacific as the Home Assistant time zone (PDT, UTC-7, in March)
@freeze_time("2026-03-16 02:00:00")  # 19:00 PDT on 2026-03-15
async def test_calendar_event_property_current_event(calendar_entity) -> None:
    """Test event property returns current event."""
    event = calendar_entity.event

    assert event is not None
    assert event.summary == "Pianobar"


@freeze_time("2026-03-16 06:00:00")  # 23:00 PDT on 2026-03-15
async def test_calendar_event_property_past_event(calendar_entity) -> None:
    """Test event property skips past events."""
    event = calendar_entity.event

    # Should skip Pianobar (ended at 22:00) and return HV71 Match
    assert event is not None
    assert event.summary == "HV71 Match"


async def test_calendar_event_property_no_data(mock_coordinator, mock_config_entry) -> None:
    """Test event property with no data."""
    mock_coordinator.data = None
    calendar_entity = KrogCompanyCalendar(mock_coordinator, mock_config_entry)

    event = calendar_entity.event
    assert event is None


async def test_calendar_event_property_empty_data(mock_coordinator, mock_config_entry) -> None:
    """Test event property with empty data."""
    mock_coordinator.data = []
    calendar_entity = KrogCompanyCalendar(mock_coordinator, mock_config_entry)

    event = calendar_entity.event
    assert event is None


@freeze_time("2026-03-14 12:00:00")
async def test_get_events_date_range(calendar_entity, mock_hass) -> None:
    """Test async_get_events returns events in date range."""
    start = datetime(2026, 3, 15, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)
    end = datetime(2026, 3, 17, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)

    events = await calendar_entity.async_get_events(mock_hass, start, end)

    assert len(events) == 2
    assert events[0].summary == "Pianobar"
    assert events[1].summary == "HV71 Match"


@freeze_time("2026-03-14 12:00:00")
async def test_get_events_all_day_event(calendar_entity, mock_hass) -> None:
    """Test all-day events are handled correctly."""
    start = datetime(2026, 3, 17, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)
    end = datetime(2026, 3, 18, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)

    events = await calendar_entity.async_get_events(mock_hass, start, end)

    assert len(events) == 1
    assert events[0].summary == "All Day Festival"
    # All-day events should use date objects
    assert events[0].start == date(2026, 3, 17)
    assert events[0].end == date(2026, 3, 18)


@freeze_time("2026-03-14 12:00:00")
async def test_get_events_past_midnight(calendar_entity, mock_hass) -> None:
    """Test events that end past midnight."""
    start = datetime(2026, 3, 18, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)
    end = datetime(2026, 3, 19, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)

    events = await calendar_entity.async_get_events(mock_hass, start, end)

    assert len(events) == 1
    assert events[0].summary == "Late Night Event"
    assert events[0].start == datetime(2026, 3, 18, 23, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)
    # End time should be next day at 2:00
    assert events[0].end == datetime(2026, 3, 19, 2, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)


@freeze_time("2026-03-14 12:00:00")
async def test_get_events_past_midnight_next_day(calendar_entity, mock_hass) -> None:
    """Test an event running past midnight is included on the day it ends."""
    start = datetime(2026, 3, 19, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)
    end = datetime(2026, 3, 20, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)

    events = await calendar_entity.async_get_events(mock_hass, start, end)

    assert len(events) == 1
    assert events[0].summary == "Late Night Event"


@pytest.fixture
def stockholm_time_zone():
    """Use Europe/Stockholm as the Home Assistant time zone."""
    original = dt_util.get_default_time_zone()
    dt_util.set_default_time_zone(dt_util.get_time_zone("Europe/Stockholm"))
    yield
    dt_util.set_default_time_zone(original)


# 23:30 UTC is 00:30 the next day in Stockholm
@freeze_time("2026-03-18 23:30:00")
async def test_calendar_event_property_after_midnight(
    calendar_entity, stockholm_time_zone
) -> None:
    """Test an event that started yesterday and runs past midnight is current."""
    event = calendar_entity.event

    assert event is not None
    assert event.summary == "Late Night Event"
    tz = dt_util.get_time_zone("Europe/Stockholm")
    assert event.start == datetime(2026, 3, 18, 23, 0, tzinfo=tz)
    assert event.end == datetime(2026, 3, 19, 2, 0, tzinfo=tz)


# 23:30 UTC is 00:30 the next day in Stockholm, after the festival day ended
@freeze_time("2026-03-17 23:30:00")
async def test_calendar_event_property_uses_ha_time_zone(
    calendar_entity, stockholm_time_zone
) -> None:
    """Test the current day is taken from the Home Assistant time zone."""
    event = calendar_entity.event

    assert event is not None
    assert event.summary == "Late Night Event"


@freeze_time("2026-03-14 12:00:00")
async def test_get_events_empty_range(calendar_entity, mock_hass) -> None:
    """Test async_get_events with no events in range."""
    start = datetime(2026, 3, 20, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)
    end = datetime(2026, 3, 25, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)

    events = await calendar_entity.async_get_events(mock_hass, start, end)

    assert len(events) == 0


@freeze_time("2026-03-14 12:00:00")
async def test_convert_to_calendar_event_timed(calendar_entity) -> None:
    """Test converting timed event."""
    from krogoco_calendar import CalendarEvent as ScrapedEvent

    scraped_event = ScrapedEvent(
        date=date(2026, 3, 20),
        title="Test Event",
        url="https://example.com/event",
        all_day=False,
        start_time="14:30",
        end_time="16:30",
    )

    ha_event = calendar_entity._convert_to_calendar_event(scraped_event)

    assert ha_event.summary == "Test Event"
    assert ha_event.start == datetime(2026, 3, 20, 14, 30, tzinfo=dt_util.DEFAULT_TIME_ZONE)
    assert ha_event.end == datetime(2026, 3, 20, 16, 30, tzinfo=dt_util.DEFAULT_TIME_ZONE)
    assert ha_event.description == "https://example.com/event"


@freeze_time("2026-03-14 12:00:00")
async def test_convert_to_calendar_event_all_day(calendar_entity) -> None:
    """Test converting all-day event."""
    from krogoco_calendar import CalendarEvent as ScrapedEvent

    scraped_event = ScrapedEvent(
        date=date(2026, 3, 20),
        title="All Day Test",
        url="https://example.com/allday",
        all_day=True,
    )

    ha_event = calendar_entity._convert_to_calendar_event(scraped_event)

    assert ha_event.summary == "All Day Test"
    assert ha_event.start == date(2026, 3, 20)
    assert ha_event.end == date(2026, 3, 21)
    assert ha_event.description == "https://example.com/allday"
