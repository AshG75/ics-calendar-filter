#!/usr/bin/env python3
import argparse
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import os


def filter_ics_by_date_range(input_file, output_file, date_from, duration_days=None):
    """
    Filter an ICS file to keep only events within a specified date range.
    
    Args:
        input_file (str): Path to input ICS file
        output_file (str): Path to output filtered ICS file
        date_from (str): Date in YYYY-MM-DD format to filter from
        duration_days (int, optional): Number of days to include after date_from.
                                       If None, includes all events after date_from.
    
    Returns:
        tuple: (success, message)
    """
    try:
        # Parse the from date
        filter_date_start = datetime.strptime(date_from, '%Y-%m-%d').date()
        
        # Calculate end date if duration is specified
        filter_date_end = None
        if duration_days is not None:
            filter_date_end = filter_date_start + timedelta(days=duration_days)
        
        # Check if input file exists
        if not os.path.isfile(input_file):
            return False, f"Error: Input file '{input_file}' not found."
        
        # Read the original ICS file
        with open(input_file, 'rb') as file:
            cal_content = file.read()
            original_cal = Calendar.from_ical(cal_content)
        
        # Create a new calendar
        new_cal = Calendar()
        
        # Copy over the main calendar properties
        for attr in ['VERSION', 'PRODID', 'CALSCALE', 'METHOD']:
            if attr in original_cal:
                new_cal.add(attr, original_cal[attr])
        
        # Find all timezone definitions
        timezones = []
        for component in original_cal.walk('VTIMEZONE'):
            timezones.append(component)
        
        # Add timezone components to the new calendar first
        for tz in timezones:
            new_cal.add_component(tz)
        
        # Filter events
        total_events = 0
        kept_events = 0
        
        # Only process VEVENT components for filtering
        for component in original_cal.walk('VEVENT'):
            total_events += 1
            
            # Get the event start date/time
            start = component.get('dtstart')
            if start:
                start_dt = start.dt
                
                # Convert datetime to date for comparison if it's a datetime object
                if hasattr(start_dt, 'date'):
                    event_date = start_dt.date()
                else:
                    event_date = start_dt  # Already a date
                
                # Check if event is within the specified range
                include_event = event_date >= filter_date_start
                if filter_date_end:
                    include_event = include_event and event_date <= filter_date_end
                
                if include_event:
                    new_cal.add_component(component)
                    kept_events += 1
        
        # Write the new calendar to the output file
        with open(output_file, 'wb') as file:
            file.write(new_cal.to_ical())
        
        # Prepare success message
        if filter_date_end:
            date_range_str = f"from {date_from} to {filter_date_end.strftime('%Y-%m-%d')}"
        else:
            date_range_str = f"from {date_from} onward"
            
        message = (f"Successfully filtered calendar. Kept {kept_events} of {total_events} events {date_range_str}.")
        return True, message
    
    except ValueError:
        return False, "Error: Invalid date format. Please use YYYY-MM-DD."
    except Exception as e:
        return False, f"Error processing calendar: {str(e)}"


def main():
    parser = argparse.ArgumentParser(
        description="Filter an ICS calendar file to include only entries within a specified date range."
    )
    parser.add_argument(
        "--input-file", "-i", 
        default="calendar.ics",
        help="Input ICS calendar file (default: calendar.ics)"
    )
    parser.add_argument(
        "--output-file", "-o", 
        default="filtered_calendar.ics",
        help="Output filtered ICS file (default: filtered_calendar.ics)"
    )
    parser.add_argument(
        "--date-from", "-d", 
        required=True,
        help="Include only events on or after this date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--duration", "-D",
        type=int,
        help="Number of days to include after the start date (default: all days)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print debug information during processing"
    )
    
    args = parser.parse_args()
    
    # If verbose mode is on, print debug info
    if args.verbose:
        try:
            # Parse the from date
            filter_date_start = datetime.strptime(args.date_from, '%Y-%m-%d').date()
            print(f"Filter start date: {filter_date_start}")
            
            if args.duration:
                filter_date_end = filter_date_start + timedelta(days=args.duration)
                print(f"Filter end date: {filter_date_end}")
            else:
                filter_date_end = None
                print("No end date specified (including all events after start date)")
            
            # Read the original ICS file
            with open(args.input_file, 'rb') as file:
                cal = Calendar.from_ical(file.read())
            
            print("\nEvents in calendar:")
            for idx, component in enumerate(cal.walk('VEVENT')):
                start = component.get('dtstart')
                if start:
                    start_dt = start.dt
                    if hasattr(start_dt, 'date'):
                        event_date = start_dt.date()
                    else:
                        event_date = start_dt
                    
                    # Check if event is within range
                    include = event_date >= filter_date_start
                    reason = "before start date" if not include else "in range"
                    
                    if filter_date_end and include:
                        include = event_date <= filter_date_end
                        if not include:
                            reason = "after end date"
                    
                    summary = component.get('summary', '[No Summary]')
                    print(f"Event {idx+1}: {summary} on {event_date} - {'KEEP' if include else 'REMOVE'} ({reason})")
        except Exception as e:
            print(f"Error during verbose inspection: {str(e)}")
    
    success, message = filter_ics_by_date_range(
        args.input_file, 
        args.output_file, 
        args.date_from,
        args.duration
    )
    
    print(message)
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())