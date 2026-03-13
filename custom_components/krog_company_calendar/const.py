"""Constants for the Krog & Co Calendar integration."""

DOMAIN = "krog_company_calendar"

CONF_CITY = "city"
CONF_BLACKLIST = "blacklist"
CONF_MONTHS = "months"

DEFAULT_MONTHS = 2
DEFAULT_REFRESH_INTERVAL = 180  # minutes

# City slug -> display name mapping
CITIES = {
    "gavle": "Gävle",
    "halmstad": "Halmstad",
    "jonkoping": "Jönköping",
    "koping": "Köping",
    "ljungby": "Ljungby",
    "uddevalla": "Uddevalla",
    "varnamo": "Värnamo",
}
