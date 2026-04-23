# Canvas LMS for Home Assistant

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Fiveol&repository=ha-canvas&category=Integration)

Bring your school assignments directly into Home Assistant. This integration creates a master calendar for your account and individual calendars for every active course you are enrolled in.

## Features
- **Master Calendar**: A single view of all upcoming assignments.
- **Per-Course Calendars**: Separate entities for each class (e.g., `calendar.name_math_101`).
- **Assignment Details**: Descriptions include the course name and points possible.
- **Easy Links**: Clicking an event in the HA Calendar will provide the URL directly to the Canvas assignment.

## Installation

### HACS (Recommended)
1. Ensure [HACS](https://hacs.xyz/) is installed.
2. Click the badge above or navigate to HACS > Integrations > 3-dot menu > Custom Repositories.
3. Add `https://github.com/Fiveol/ha-canvas` with category `Integration`.
4. Search for "Canvas Student" and install.
5. Restart Home Assistant.

### Manual
1. Download the `canvas_student` folder from `custom_components`.
2. Paste it into your Home Assistant `/config/custom_components/` directory.
3. Restart Home Assistant.

## Configuration
1. Go to **Settings > Devices & Services > Add Integration**.
2. Search for **Canvas Student**.
3. **Base URL**: Enter your school's Canvas URL (e.g., `https://canvas.instructure.com` or `https://university.instructure.com`).
4. **Access Token**: 
   - Log into Canvas.
   - Go to **Account > Settings**.
   - Scroll down to **Approved Integrations** and click **+ New Access Token**.
   - Copy and paste that token into Home Assistant.

## Limitations
- **Rolling Window**: This integration uses the "Upcoming Events" endpoint. It displays assignments due in the near future (typically the next few weeks). It is not intended for historical tracking or the entire semester at once.
- **Sync Interval**: Data refreshes every 15 minutes to keep your dashboard updated without stressing the Canvas API.

---
*Disclaimer: This integration is not affiliated with or endorsed by Instructure/Canvas LMS.*