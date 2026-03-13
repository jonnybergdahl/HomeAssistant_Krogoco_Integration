"""Data coordinator for Krog & Co Calendar."""
from datetime import timedelta
import logging

from krog_company_ics import KrogocoIcs
import requests

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_REFRESH_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class KrogCompanyCalendarCoordinator(DataUpdateCoordinator):
    """Coordinator to manage fetching Krog & Co calendar data."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        city: str,
        months: int,
        blacklist: list[str],
    ) -> None:
        """Initialize the coordinator."""
        self.city = city
        self.months = months
        self.blacklist = blacklist
        self.url = f"https://krogoco.se/{city}/kalender/"

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=DEFAULT_REFRESH_INTERVAL),
            config_entry=entry,
        )

    async def _async_update_data(self):
        """Fetch data from Krog & Co website."""
        try:
            scraper = KrogocoIcs(self.url, self.months, self.blacklist)
            events = await self.hass.async_add_executor_job(scraper.scrape_events)
            _LOGGER.debug("Fetched %d events for %s", len(events), self.city)
            return events
        except requests.RequestException as err:
            raise UpdateFailed(f"Error fetching data from {self.url}: {err}") from err
