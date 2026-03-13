# Krog & Co Calendar - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

A Home Assistant custom integration that exposes events from Krog & Co restaurants in Sweden as a native calendar entity.

## Features

- 🗓️ Native Home Assistant calendar entity
- 🏙️ Support for multiple cities: Gävle, Halmstad, Jönköping, Köping, Ljungby, Uddevalla, Värnamo
- 🚫 Blacklist support to filter out unwanted events
- ⏰ All-day and timed event support
- 🔄 Automatic updates every 3 hours
- ⚙️ Easy configuration through the UI
- 📱 Works with Home Assistant calendar card and automations

## Installation

### HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jonnybergdahl&repository=HomeAssistant_Krogoco_Integration&category=Integration)

Or install manually through HACS:

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/jonnybergdahl/HomeAssistant_Krogoco_Integration`
6. Select category: "Integration"
7. Click "Add"
8. Find "Krog & Co Calendar" in the list and click "Download"
9. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/krog_company_calendar` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=krog_company_calendar)

Or set up manually:

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Krog & Co Calendar**
4. Select your city from the dropdown
5. (Optional) Add blacklist terms separated by commas (e.g., `hv71,matchb` to exclude HV71 hockey matches)
6. Click **Submit**

### Options

After adding the integration, you can modify settings:

1. Go to **Settings** → **Devices & Services**
2. Find **Krog & Co Calendar**
3. Click **Configure**
4. Update:
   - **Blacklist**: Comma-separated terms to exclude events
   - **Months ahead**: How many months to fetch (1-12, default: 2)

## Usage

### Calendar Card

Add the calendar to your dashboard using the calendar card:

```yaml
type: calendar
entities:
  - calendar.krog_company_calendar_jonkoping
```

### Automations

Trigger automations based on upcoming events:

```yaml
automation:
  - alias: "Notify about Pianobar tonight"
    trigger:
      - platform: calendar
        entity_id: calendar.krog_company_calendar_jonkoping
        event: start
        offset: "-2:00:00"
    condition:
      - condition: template
        value_template: "{{ 'pianobar' in trigger.calendar_event.summary.lower() }}"
    action:
      - service: notify.mobile_app
        data:
          title: "Event Tonight"
          message: "{{ trigger.calendar_event.summary }} starts at {{ trigger.calendar_event.start }}"
```

### Accessing Event URLs

Each event includes the Krog & Co event page URL in the description field, accessible in automations:

```yaml
{{ trigger.calendar_event.description }}
```

## Supported Cities

- Gävle (`gavle`)
- Halmstad (`halmstad`)
- Jönköping (`jonkoping`)
- Köping (`koping`)
- Ljungby (`ljungby`)
- Uddevalla (`uddevalla`)
- Värnamo (`varnamo`)

## Troubleshooting

### Events not showing

1. Check the integration logs in **Settings** → **System** → **Logs**
2. Verify the Krog & Co website is accessible: `https://krogoco.se/{city}/kalender/`
3. Try reloading the integration

### Connection errors

- Ensure your Home Assistant instance has internet access
- Check if the Krog & Co website is online
- Verify your firewall isn't blocking the connection

## Development

Built using:
- [`krog-company-ics`](https://github.com/jonnybergdahl/krog-company-ics) library for event scraping
- Home Assistant's `CalendarEntity` platform
- `DataUpdateCoordinator` for efficient polling

## License

MIT License

## Credits

Created by [@jonnybergdahl](https://github.com/jonnybergdahl)
