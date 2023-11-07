import datetime
import googleapiclient.discovery
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Set up the credentials for accessing Google Calendar
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
# Create a Calendar API client
service = googleapiclient.discovery.build('calendar', 'v3', credentials=creds)

# Define the calendar IDs for Calendar A and Calendar B
calendar_a_id = 'c_6622c0bc68514f029191e4355e7580ac66ffde0c120cdb2801159391fefc58ff@group.calendar.google.com'
calendar_b_id = 'c_0433d8d93c825f97acf6188e15797027de71229ef946dd6e1b1001b538112039@group.calendar.google.com'

# Get events from Calendar A
now = datetime.datetime.utcnow()
events_result = service.events().list(
    calendarId=calendar_a_id,
    timeMin=now.isoformat() + 'Z',
    maxResults=10,  # You can adjust the number of events to retrieve
    singleEvents=True,
    orderBy='startTime',
).execute()

events_a = events_result.get('items', [])

# Filter out events in Calendar A created by Calendar A
events_created_by_a = [event for event in events_a if event['organizer']['email'] == calendar_a_id]

# Now, events_created_by_a contains events in Calendar A created by Calendar A
print("Events in Calendar A created by Calendar A:")
for event in events_created_by_a:
    print(event['summary'])
