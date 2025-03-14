#!/usr/bin/env python3
import json
from datetime import datetime, timedelta
from icalendar import Calendar
import pytz
import argparse
import sys
import re

def parse_ics_to_json(ics_file_path):
    """
    Parse an ICS file and convert each event to JSON format.
    
    Args:
        ics_file_path (str): Path to the ICS file
        
    Returns:
        list: List of dictionaries containing event information
    """
    try:
        # Read with encoding that handles BOM and special characters
        with open(ics_file_path, 'rb') as file:
            content = file.read()
            # Try to handle different encodings
            try:
                # First try UTF-8
                cal_content = content.decode('utf-8').replace('\ufeff', '')
            except UnicodeDecodeError:
                try:
                    # Then try Latin-1 (more permissive)
                    cal_content = content.decode('latin-1').replace('\ufeff', '')
                except UnicodeDecodeError:
                    # Last resort: just use ASCII with replacement
                    cal_content = content.decode('ascii', errors='replace').replace('\ufeff', '')
            
            # Clean the content to ensure it's ASCII-compatible
            cal_content = ''.join(c if ord(c) < 128 else '?' for c in cal_content)
            
            # Parse the calendar
            cal = Calendar.from_ical(cal_content.encode('ascii', errors='replace'))
    except Exception as e:
        print(f"Error reading ICS file: {e}", file=sys.stderr)
        return []
    
    events = []
    
    for component in cal.walk():
        if component.name == "VEVENT":
            event = {}
            
            # Get event title (summary)
            if 'SUMMARY' in component:
                event['title'] = str(component.get('SUMMARY'))
            else:
                event['title'] = "No Title"
            
            # Get start time
            start = component.get('DTSTART').dt
            if isinstance(start, datetime):
                # Convert to ISO format if it's a datetime
                event['start_time'] = start.isoformat()
            else:
                # If it's a date, convert to ISO and set time to midnight
                event['start_time'] = datetime.combine(start, datetime.min.time()).isoformat()
            
            # Calculate duration
            if 'DTEND' in component:
                end = component.get('DTEND').dt
                if isinstance(end, datetime) and isinstance(start, datetime):
                    duration = end - start
                    event['duration'] = str(duration)
                    # Add duration in minutes for easier processing
                    event['duration_minutes'] = int(duration.total_seconds() / 60)
                else:
                    # For all-day events, duration is in days
                    if isinstance(end, datetime):
                        end = end.date()
                    if isinstance(start, datetime):
                        start = start.date()
                    duration_days = (end - start).days
                    event['duration'] = f"{duration_days} days"
                    event['duration_minutes'] = duration_days * 24 * 60
            elif 'DURATION' in component:
                event['duration'] = str(component.get('DURATION'))
                # Try to convert to minutes if possible
                duration_str = str(component.get('DURATION'))
                # Parse the duration string (PT1H30M format)
                hours = re.search(r'(\d+)H', duration_str)
                minutes = re.search(r'(\d+)M', duration_str)
                seconds = re.search(r'(\d+)S', duration_str)
                
                total_minutes = 0
                if hours:
                    total_minutes += int(hours.group(1)) * 60
                if minutes:
                    total_minutes += int(minutes.group(1))
                if seconds:
                    total_minutes += int(seconds.group(1)) / 60
                
                event['duration_minutes'] = total_minutes
            else:
                event['duration'] = "Unknown"
                event['duration_minutes'] = 0
            
            # Get attendees and their status
            attendees = []
            
            # Debug information
            print(f"Event: {event.get('title', 'No Title')}")
            print(f"Type of ATTENDEE: {type(component.get('ATTENDEE', []))}")
            attendee_list = component.get('ATTENDEE', [])
            if not isinstance(attendee_list, list):
                attendee_list = [attendee_list]
            
            for i, att in enumerate(attendee_list):
                print(f"Attendee {i} type: {type(att)}, value: {att}")
            
            for attendee in attendee_list:
                attendee_dict = {}
                
                # Extract email from mailto: format
                email = str(attendee)
                if email.startswith("mailto:"):
                    email = email[7:]  # Remove "mailto:" prefix
                attendee_dict['email'] = email
                
                # Get acceptance status
                if hasattr(attendee, 'params'):
                    params = attendee.params
                    if 'PARTSTAT' in params:
                        attendee_dict['status'] = str(params['PARTSTAT'])
                    else:
                        attendee_dict['status'] = "UNKNOWN"
                    
                    # Get attendee name if available
                    if 'CN' in params:
                        attendee_dict['name'] = str(params['CN'])
                else:
                    attendee_dict['status'] = "UNKNOWN"
                
                attendees.append(attendee_dict)
            
            event['attendees'] = attendees
            
            # Get notes/description
            if 'DESCRIPTION' in component:
                event['notes'] = str(component.get('DESCRIPTION'))
            else:
                event['notes'] = ""
            
            # Get location if available
            if 'LOCATION' in component:
                event['location'] = str(component.get('LOCATION'))
            
            # Get UID for unique identification
            if 'UID' in component:
                event['uid'] = str(component.get('UID'))
            
            # Determine meeting type (internal or external)
            internal_domains = ['ten10.com', 'scalefactory.com', 'thetestpeople.com', 'group.calendar.google.com', 'resource.calendar.google.com']
            has_external_attendees = False
            
            for attendee in attendees:
                email = attendee.get('email', '')
                is_internal_email = False
                
                for domain in internal_domains:
                    if email and email.lower().endswith('@' + domain):
                        is_internal_email = True
                        break
                
                if email and not is_internal_email:
                    has_external_attendees = True
                    break
            
            event['meeting_type'] = 'external' if has_external_attendees else 'internal'
            
            events.append(event)
    
    # Sort events by start time (oldest first)
    def get_event_start_time(event):
        start_time = event.get('start_time', '')
        if start_time:
            try:
                # Try to parse the ISO format date
                dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                
                # Make sure it's offset-naive for consistent comparison
                if dt.tzinfo is not None:
                    # Convert to UTC then remove timezone info
                    dt = dt.astimezone(pytz.UTC).replace(tzinfo=None)
                return dt
            except (ValueError, TypeError):
                # If parsing fails, return a distant future date to place it at the end
                return datetime.max
        return datetime.max
    
    sorted_events = sorted(events, key=get_event_start_time)
    return sorted_events

def main():
    parser = argparse.ArgumentParser(description='Convert ICS calendar file to JSON')
    parser.add_argument('ics_file', help='Path to the ICS file')
    parser.add_argument('--output', '-o', help='Output JSON file (default: stdout)')
    parser.add_argument('--pretty', '-p', action='store_true', help='Pretty print JSON output')
    
    args = parser.parse_args()
    
    events = parse_ics_to_json(args.ics_file)
    
    # Clean Unicode characters that might cause issues
    def clean_event(event):
        for key, value in list(event.items()):
            if isinstance(value, str):
                # Replace BOM and other problematic characters with safer alternatives
                cleaned_value = value.replace('\ufeff', '')  # Remove BOM specifically
                cleaned_value = ''.join(c if ord(c) < 128 else '?' for c in cleaned_value)  # ASCII only
                event[key] = cleaned_value
            elif key == 'attendees' and isinstance(value, list):
                for attendee in value:
                    for att_key, att_value in list(attendee.items()):
                        if isinstance(att_value, str):
                            # Same cleaning for attendee values
                            cleaned_att_value = att_value.replace('\ufeff', '')
                            cleaned_att_value = ''.join(c if ord(c) < 128 else '?' for c in cleaned_att_value)
                            attendee[att_key] = cleaned_att_value
        return event
    
    # Apply cleaning to all events
    cleaned_events = [clean_event(event) for event in events]
    
    if args.output:
        try:
            # Use 'ascii' encoding to ensure compatibility
            with open(args.output, 'w', encoding='ascii', errors='replace') as file:
                if args.pretty:
                    json.dump(cleaned_events, file, indent=2, ensure_ascii=True)
                else:
                    json.dump(cleaned_events, file, ensure_ascii=True)
        except Exception as e:
            print(f"Error writing to file: {e}")
            print("Trying alternate approach...")
            # Fallback to direct string manipulation
            json_str = json.dumps(cleaned_events, indent=2 if args.pretty else None, ensure_ascii=True)
            with open(args.output, 'w', encoding='ascii', errors='replace') as file:
                file.write(json_str)
    else:
        json_str = json.dumps(cleaned_events, indent=2 if args.pretty else None, ensure_ascii=True)
        print(json_str)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()