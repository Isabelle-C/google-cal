from __future__ import print_function

import datetime
import dateutil.parser
from pytz import timezone
import os.path
import yaml

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def parse_date(date, convert_timezone):
    parsed_date = dateutil.parser.isoparse(date)
    
    if convert_timezone!=None:
        return parsed_date.astimezone(timezone(convert_timezone))

    return parsed_date

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print(f'Getting the upcoming {max_results} events')
        events_result = service.events().list(calendarId=calendar_id, timeMin=now,maxResults=max_results, singleEvents=True,
        orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        with open(output_file, 'w') as file:
            events_to_write = []
            # Prints the events that has the event name
            for event in events:
                if event['summary'] == event_name:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    end = event['end'].get('dateTime', event['end'].get('date'))
                    
                    event_start_date = parse_date(start, convert_timezone)

                    if start_date <= event_start_date <= end_date:
                        
                        start_time_day = event_start_date.strftime('%A %m/%d')
                        start_time_time = event_start_date.strftime('%I:%M %p').lstrip("0")

                        event_end_date = parse_date(end, convert_timezone)
                        six_pm = datetime.datetime(event_end_date.year, event_end_date.month, event_end_date.day, 18, 0, 0)
                        
                        if event_end_date.time() > six_pm.time():
                            end_d = '6:00 PM'
                        else:
                            end_d = event_end_date.strftime('%I:%M %p').lstrip("0")

                        events_to_write.append(f"- {start_time_day} {start_time_time} - {end_d}")

            for line in events_to_write:
                file.write(line + '\n')

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    filename = "./config.yaml"
    with open(filename, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    max_results = config["max_results"]
    calendar_id = config["calendar_id"]
    event_name = config["event_name"]

    time_range = config["time_range"]
    start_date = dateutil.parser.isoparse(time_range["start"])
    end_date = dateutil.parser.isoparse(time_range["end"])
    convert_timezone = config["timezone"]

    output_file=config["output_file"]

    main()