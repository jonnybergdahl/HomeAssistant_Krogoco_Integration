"""Calendar entity for Krog & Co Calendar."""
from datetime import datetime, time, timedelta
import logging

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import CITIES, CONF_CITY, DOMAIN
from .coordinator import KrogCompanyCalendarCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Krog & Co Calendar entity."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([KrogCompanyCalendar(coordinator, entry)], True)


class KrogCompanyCalendar(CoordinatorEntity[KrogCompanyCalendarCoordinator], CalendarEntity):
    """Representation of a Krog & Co Calendar."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: KrogCompanyCalendarCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the calendar entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{coordinator.city}"
        self._city = coordinator.city
        self._attr_name = CITIES.get(coordinator.city, coordinator.city.capitalize())

        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.city)},
            "name": f"Krog & Co {self._attr_name}",
            "manufacturer": "Krog & Co",
        }

    def _calendar_events(self) -> list[CalendarEvent]:
        """Return all scraped events converted to HA calendar events."""
        if not self.coordinator.data:
            return []
        return [self._convert_to_calendar_event(e) for e in self.coordinator.data]

    @property
    def event(self) -> CalendarEvent | None:
        """Return the current or next event."""
        now = dt_util.now()
        # Events that haven't ended yet, including ones that started
        # yesterday and run past midnight
        upcoming = [e for e in self._calendar_events() if e.end_datetime_local > now]
        if not upcoming:
            return None
        return min(upcoming, key=lambda e: e.start_datetime_local)

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events that overlap a datetime range."""
        return [
            event
            for event in self._calendar_events()
            if event.start_datetime_local < end_date
            and event.end_datetime_local > start_date
        ]

    def _convert_to_calendar_event(self, scraped_event) -> CalendarEvent:
        """Convert a krogoco_calendar CalendarEvent to HA CalendarEvent."""
        # All-day events
        if scraped_event.all_day or not scraped_event.start_time:
            return CalendarEvent(
                start=scraped_event.date,
                end=scraped_event.date + timedelta(days=1),
                summary=scraped_event.title,
                description=scraped_event.url,
            )

        start_time = _parse_time(scraped_event.start_time)
        # If no end time, assume end of day
        end_time = _parse_time(scraped_event.end_time) if scraped_event.end_time else time(23, 59)

        tz = dt_util.get_default_time_zone()
        start_dt = datetime.combine(scraped_event.date, start_time, tzinfo=tz)
        end_dt = datetime.combine(scraped_event.date, end_time, tzinfo=tz)

        # Handle end times past midnight
        if end_time < start_time:
            end_dt += timedelta(days=1)

        return CalendarEvent(
            start=start_dt,
            end=end_dt,
            summary=scraped_event.title,
            description=scraped_event.url,
        )


def _parse_time(value: time | str) -> time:
    """Return a time from either a time object or an ISO time string."""
    return value if isinstance(value, time) else time.fromisoformat(value)
