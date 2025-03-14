# ICS Calendar Utils

A set of utilities to process google calendar events.  Assumes an intial extraction from Google Calendar as an ICS file

# ICS Calendar Date Filter

A Python utility to filter ICS calendar files by date range. Google Calendar is able to extract only an ICS for a full calendar
This tool allows you to extract events from a specific date forward or for a specific duration.

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

# ICS Calendar Parser

A toolkit for parsing ICS calendar files and converting events to structured formats (JSON and CSV).

## Overview

This project consists of two tools:

1. **ics_parser.py**: Parses ICS (iCalendar) files and converts events to JSON
2. **json_to_csv_converter.py**: Converts the JSON output to CSV format

Together, these tools allow you to extract calendar data and analyze it in a format that's easy to work with.

## Features

- Extract event details including:
  - Title
  - Start time
  - Duration
  - Attendees and their status
  - Notes
  - Location
- Identify internal vs external meetings based on attendee domains
- Sort events chronologically
- Handle special characters and encoding issues
- Output to JSON and/or CSV formats

## Requirements

- Python 3.6+
- Python packages:
  - icalendar
  - pytz

Install the dependencies:

```bash
pip install icalendar pytz
```

## Usage

### Step 1: Convert ICS to JSON

```bash
python ics_parser.py calendar.ics -o events.json -p
```

Parameters:
- `calendar.ics`: Path to the input ICS file
- `-o events.json`: Output JSON file (optional, default is stdout)
- `-p`: Pretty print JSON (optional)

### Step 2: Convert JSON to CSV

```bash
python json_to_csv_converter.py events.json -o events.csv
```

Parameters:
- `events.json`: Path to the input JSON file
- `-o events.csv`: Output CSV file (optional, default is events.csv)

## JSON Output Format

The JSON output includes detailed information about each event:

```json
[
  {
    "title": "Meeting with Team",
    "start_time": "2023-03-15T10:00:00",
    "duration": "1:00:00",
    "duration_minutes": 60,
    "attendees": [
      {
        "email": "person@example.com",
        "status": "ACCEPTED",
        "name": "Person Name"
      }
    ],
    "notes": "Meeting notes here",
    "location": "Conference Room A",
    "meeting_type": "internal"
  }
]
```

## CSV Output Format

The CSV output includes the following columns:
- datetime
- duration
- title
- meeting_type
- attendee_emails (semicolon separated)

## Internal vs External Meeting Classification

Meetings are classified as:
- **Internal**: When all attendees have email addresses from the following domains:
  - ten10.com
  - scalefactory.com
  - thetestpeople.com
- **External**: When at least one attendee has an email address from any other domain

## Handling Special Characters

The tools include special handling for Unicode characters and various encodings to ensure compatibility with different systems.

## Error Handling

Both tools include comprehensive error handling for issues such as:
- Invalid ICS files
- Encoding problems
- Date parsing issues
- Missing required fields

## License

[MIT License](LICENSE)
