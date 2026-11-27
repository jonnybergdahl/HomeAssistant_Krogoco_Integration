# Krog & Co Calendar - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

A Home Assistant custom integration that exposes events from Krog & Co restaurants in Sweden as a native calendar entity.

## Features

- 🗓️ Native Home Assistant calendar entity
- 🏙️ Support for multiple cities: Gävle, Halmstad, Jönköping, Köping, Ljungby, Uddevalla, Värnamo
- 🚫 Blacklist support to filter out unwanted events
- ⏰ All-day and timed events, with start and end times read from the event titles (events running past midnight end the next day)
- 🔄 Automatic updates every 3 hours
- ⚙️ Easy configuration through the UI
- 📱 Works with Home Assistant calendar card and automations

## Installation

### Marketplace (recommended)

Krog & Co Calendar can be installed from the Home Assistant Marketplace (Home Assistant 2026.11 or newer). It isn't listed in the default store yet, so add it as a custom repository first.

1. Go to **Settings** > **Marketplace**
2. Open the menu (⋮), select **Custom repositories**, add `https://github.com/jonnybergdahl/HomeAssistant_Krogoco_Integration` with type **Integration**, and select **Add**
3. Search for **Krog & Co Calendar** and open it
4. Select **Install**, check the version, and select **Install** again

Or click the button to open Krog & Co Calendar directly in the Marketplace. It offers to add the repository as a custom repository for you:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jonnybergdahl&category=Integration&repository=HomeAssistant_Krogoco_Integration)

No restart is needed. Home Assistant goes straight to the setup flow described below.

> On Home Assistant 2024.12 to 2026.10, install Krog & Co Calendar through HACS instead: add the repository as a custom repository (menu ⋮, **Custom repositories**, type **Integration**), search for **Krog & Co Calendar**, click **Download**, then restart Home Assistant.

### Manual

1. Copy the `custom_components/krog_company_calendar` folder into your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Setup

Click the button to add a Krog & Co calendar to Home Assistant.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=krog_company_calendar)

You can also set it up manually:

1. Go to **Settings** > **Devices & services** > **Add integration**
2. Search for **Krog & Co Calendar**
3. Select your city, and optionally add blacklist terms separated by commas (e.g. `hv71,match` to exclude HV71 hockey matches)
4. Click **Submit**

Add each city you want the same way. Each city gets its own device and calendar.

> To change the blacklist or how many months ahead to fetch (1-12, default 2), open the integration's **Configure** action.

## Usage

### Calendar Card

Add the calendar to your dashboard using the calendar card:

```yaml
type: calendar
entities:
  - calendar.krog_co_jonkoping_jonkoping
```

The entity ID is `calendar.krog_co_<city>_<city>`, for example `calendar.krog_co_jonkoping_jonkoping` for Jönköping.

### Automations

Trigger automations based on upcoming events:

```yaml
alias: "Notify about Pianobar tonight"
triggers:
  - trigger: calendar
    entity_id: calendar.krog_co_jonkoping_jonkoping
    event: start
    offset: "-2:00:00"
conditions:
  - condition: template
    value_template: "{{ 'pianobar' in trigger.calendar_event.summary.lower() }}"
actions:
  - action: notify.mobile_app_your_phone
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
- [`krogoco-calendar`](https://pypi.org/project/krogoco-calendar/) library for event scraping ([source](https://github.com/jonnybergdahl/Python-krogoco-calendar), [docs](https://jonnybergdahl.github.io/krogoco-calendar/))
- Home Assistant's `CalendarEntity` platform
- `DataUpdateCoordinator` for efficient polling

## License

MIT License

## Credits

Created by [@jonnybergdahl](https://github.com/jonnybergdahl)
