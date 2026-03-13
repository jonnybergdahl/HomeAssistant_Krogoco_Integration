"""Calendar entity for Krog & Co Calendar."""
from datetime import date, datetime, time, timedelta
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

    @property
    def event(self) -> CalendarEvent | None:
        """Return the current or next event."""
        if not self.coordinator.data:
            return None

        today = date.today()
        now = dt_util.now()

        for scraped_event in self.coordinator.data:
            # Skip events in the past
            if scraped_event.date < today:
                continue

            # For events today with times, check if they're currently active or upcoming
            if scraped_event.date == today and scraped_event.start_time and not scraped_event.all_day:
                start_time = time.fromisoformat(scraped_event.start_time)
                event_start = datetime.combine(
                    scraped_event.date,
                    start_time,
                    tzinfo=dt_util.DEFAULT_TIME_ZONE,
                )
                # If we have an end time, use it; otherwise assume event is still relevant
                if scraped_event.end_time:
                    end_time = time.fromisoformat(scraped_event.end_time)
                    event_end = datetime.combine(
                        scraped_event.date,
                        end_time,
                        tzinfo=dt_util.DEFAULT_TIME_ZONE,
                    )
                    # Handle end times past midnight
                    if end_time < start_time:
                        event_end += timedelta(days=1)

                    # Skip if event has already ended
                    if now > event_end:
                        continue

            # Convert to HA CalendarEvent
            return self._convert_to_calendar_event(scraped_event)

        return None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        events = []

        if not self.coordinator.data:
            return events

        for scraped_event in self.coordinator.data:
            # Filter events within the requested date range
            if scraped_event.date < start_date.date() or scraped_event.date >= end_date.date():
                continue

            events.append(self._convert_to_calendar_event(scraped_event))

        return events

    def _convert_to_calendar_event(self, scraped_event) -> CalendarEvent:
        """Convert a krog_company_ics CalendarEvent to HA CalendarEvent."""
        # All-day events
        if scraped_event.all_day or not scraped_event.start_time:
            return CalendarEvent(
                start=scraped_event.date,
                end=scraped_event.date + timedelta(days=1),
                summary=scraped_event.title,
                description=scraped_event.url,
            )

        # Timed events - convert time strings to time objects
        start_time = time.fromisoformat(scraped_event.start_time)
        end_time = time.fromisoformat(scraped_event.end_time)

        start_dt = datetime.combine(
            scraped_event.date,
            start_time,
            tzinfo=dt_util.DEFAULT_TIME_ZONE,
        )

        end_dt = datetime.combine(
            scraped_event.date,
            end_time,
            tzinfo=dt_util.DEFAULT_TIME_ZONE,
        )

        # Handle end times past midnight
        if end_time < start_time:
            end_dt += timedelta(days=1)

        return CalendarEvent(
            start=start_dt,
            end=end_dt,
            summary=scraped_event.title,
            description=scraped_event.url,
        )
