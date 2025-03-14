#!/usr/bin/env python3
import json
import csv
import argparse
import sys
from datetime import datetime

def convert_json_to_csv(json_file_path, csv_file_path):
    """
    Convert calendar events JSON file to CSV format.
    
    Args:
        json_file_path (str): Path to the input JSON file
        csv_file_path (str): Path to the output CSV file
    """
    try:
        with open(json_file_path, 'r') as file:
            events = json.load(file)
    except Exception as e:
        print(f"Error reading JSON file: {e}", file=sys.stderr)
        return False
    
    if not events or not isinstance(events, list):
        print("Error: No events found or invalid JSON format", file=sys.stderr)
        return False
    
    try:
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            # Define CSV field names
            fieldnames = ['datetime', 'meeting_type', 'duration', 'title', 'meeting_type', 'attendee_emails']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write the header row
            writer.writeheader()
            
            # Process each event
            for event in events:
                # Format datetime
                start_time = event.get('start_time', '')
                datetime_str = start_time
                try:
                    # Try to convert ISO format to more readable format
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    datetime_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError, AttributeError):
                    # If conversion fails, use the original string
                    pass
                
                # Format duration in minutes
                duration = event.get('duration_minutes', '')
                
                # Get title
                title = event.get('title', 'No Title')
                
                # Get meeting type
                meeting_type = event.get('meeting_type', 'unknown')
                
                # Join all attendee emails with semicolons
                attendee_emails = []
                for attendee in event.get('attendees', []):
                    email = attendee.get('email', '').strip()
                    if email:
                        attendee_emails.append(email)
                
                attendee_emails_str = ';'.join(attendee_emails)
                
                # Write the row
                writer.writerow({
                    'datetime': datetime_str,
                    'duration': duration,
                    'title': title,
                    'meeting_type': meeting_type,
                    'attendee_emails': attendee_emails_str
                })
                
        print(f"Successfully converted {len(events)} events to CSV: {csv_file_path}")
        return True
        
    except Exception as e:
        print(f"Error writing CSV file: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description='Convert calendar events JSON to CSV')
    parser.add_argument('json_file', help='Path to the input JSON file')
    parser.add_argument('--output', '-o', help='Output CSV file (default: events.csv)', default='events.csv')
    
    args = parser.parse_args()
    
    convert_json_to_csv(args.json_file, args.output)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()