# ICS Calendar Date Filter

A Python utility to filter ICS calendar files by date range. This tool allows you to extract events from a specific date forward or for a specific duration.

## Features

- Filter calendar events by start date
- Optionally limit to a specific number of days
- Preserve calendar properties and formatting
- Maintain timezone information
- Generate detailed statistics about filtered events
- Debug mode to track which events are included/excluded

## Requirements

- Python 3.6+
- icalendar library

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/ics-date-filter.git
   cd ics-date-filter
   ```

2. Install the required dependency:
   ```bash
   pip install icalendar
   ```

## Usage

### Basic Usage

Filter all events from March 1, 2025 onward:

```bash
python ics-date-filter.py --date-from 2025-03-01
```

### Filtering with Duration

Filter events for a specific 7-day period:

```bash
python ics-date-filter.py --date-from 2025-03-01 --duration 7
```

This will include events from March 1, 2025 through March 8, 2025 (inclusive).

### Custom Input/Output Files

```bash
python ics-date-filter.py --input-file my_calendar.ics --output-file filtered_calendar.ics --date-from 2025-03-01
```

### All Options

```bash
python ics-date-filter.py --help
```

This displays all available options:

```
usage: ics-date-filter.py [-h] [--input-file INPUT_FILE] [--output-file OUTPUT_FILE] --date-from DATE_FROM [--duration DURATION] [--verbose]

Filter an ICS calendar file to include only entries within a specified date range.

options:
  -h, --help            show this help message and exit
  --input-file INPUT_FILE, -i INPUT_FILE
                        Input ICS calendar file (default: calendar.ics)
  --output-file OUTPUT_FILE, -o OUTPUT_FILE
                        Output filtered ICS file (default: filtered_calendar.ics)
  --date-from DATE_FROM, -d DATE_FROM
                        Include only events on or after this date (YYYY-MM-DD)
  --duration DURATION, -D DURATION
                        Number of days to include after the start date (default: all days)
  --verbose, -v         Print debug information during processing
```

## Debugging

If your calendar isn't being filtered as expected, use the verbose flag to see details about each event:

```bash
python ics-date-filter.py --date-from 2025-03-01 --verbose
```

This will print information about each event including:
- The event summary
- Its date
- Whether it will be kept or removed based on your filter conditions
- The reason for inclusion or exclusion

## Examples

### Extract Next Week's Calendar

```bash
python ics-date-filter.py -i full_year.ics -o next_week.ics -d 2025-03-15 -D 7
```

### Create a Calendar for the Next 90 Days

```bash
python ics-date-filter.py -i full_year.ics -o next_quarter.ics -d 2025-03-01 -D 90
```

### Extract All Future Events

```bash
python ics-date-filter.py -i calendar.ics -o future_events.ics -d 2025-03-01
```

## How It Works

The script:

1. Reads the original ICS file using the `icalendar` library
2. Creates a new calendar with the same properties as the original
3. Preserves timezone definitions
4. For each event in the original calendar:
   - Checks if the start date is within the specified range
   - Adds it to the new calendar if it passes the filter
5. Writes the filtered calendar to the output file

## Limitations

- All-day events are handled as date objects
- The filter is based on the event start date only (events that start before the filter date but end after it are excluded)
- Recurring events are handled as individual events as they appear in the ICS file

## License

[MIT License](LICENSE)
