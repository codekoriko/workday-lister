import os
import pickle
from collections import namedtuple
from datetime import date, datetime, timedelta
from logging import getLogger
from pathlib import Path
from typing import Dict, List, Optional

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

from workday_lister.types import MarkedDays, Period

# Replace 'my_module' with the actual name of the module
logger = getLogger(__name__)

SCOPES = (
    'https://www.googleapis.com/auth/calendar.readonly',
)


class CalendarService:
    def __init__(
        self,
        calendar_id: str,
    ):
        self.calendar_id = calendar_id
        self.service = self.get_calendar_service()

    def get_calendar_service(self):
        creds = None
        settings_path = Path(os.path.expanduser('~')) / '.workday_lister/'
        # Define the path for token.pickle using pathlib
        token_path = settings_path / 'token.pickle'

        # The file token.pickle stores the user's access and refresh tokens,
        # and is created automatically when the authorization flow completes
        # for the first time.
        if token_path.exists():
            with open(token_path, 'rb') as token_load:
                creds = pickle.load(token_load)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Define the path for credentials.json
                credentials_path = settings_path / 'credentials.json'
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path,
                    SCOPES,
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(token_path, 'wb') as token_save:
                pickle.dump(creds, token_save)

        return build('calendar', 'v3', credentials=creds)

    def date_str_safe_get(self, date_obj: Dict[str, str]) -> date:
        date_str = None
        if 'dateTime' in date_obj:
            date_str = date_obj['dateTime'].split('T')[0]
        else:
            date_str = date_obj['date']
        return datetime.fromisoformat(date_str).date()

    def get_event_period(self, event: Dict[str, Dict[str, str]]) -> Period:
        start_date = self.date_str_safe_get(event['start'])
        end_date = self.date_str_safe_get(event['end'])
        return Period(start_date, end_date)

    def get_days(self, period: Period) -> MarkedDays:
        marked_days: MarkedDays = {}
        time_min = period.start.isoformat() + 'T00:00:00Z'
        time_max = period.end.isoformat() + 'T23:59:59Z'
        events_result = self.service.events().list(
            calendarId=self.calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime',
        ).execute()
        events = events_result.get('items', [])

        if events:
            for event in events:
                event_period = self.get_event_period(event)
                current_date = event_period.start
                while current_date < event_period.end:
                    marked_days[current_date] = event['description']
                    current_date += timedelta(days=1)
        else:
            logger.info('No upcoming events found.')
        if marked_days:
            logger.info(f'Found the following vacations: {marked_days}')
        else:
            logger.info('No days off were Found')
        return marked_days
