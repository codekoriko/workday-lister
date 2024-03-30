import os
import pickle
from collections import namedtuple
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional

from codecorico_invoicer.logger import get_logger
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

from workday_lister.types import DaysOff, Period

# Replace 'my_module' with the actual name of the module
logger = get_logger(__name__)

SCOPES = (
    'https://www.googleapis.com/auth/calendar.readonly',
)

class CalendarService:
    def __init__(self,
        vacation_calendar_id: str,
        holiday_calendar_ids: Optional[List[str]],
    ):
        self.vacation_calendar_id = vacation_calendar_id
        self.holiday_calendar_ids = holiday_calendar_ids
        self.service = self.get_calendar_service()

    def get_calendar_service(self):
        creds = None
        settings_path = Path(os.path.expanduser('~')) / '.workday_lister/'
        # Define the path for token.pickle using pathlib
        token_path = settings_path / 'token.pickle'

        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
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

    def get_vacation(self, period: Period) -> DaysOff:
        vacation = None
        days_off: DaysOff = {}
        time_min = period.start.isoformat() + 'T00:00:00Z'
        time_max = period.end.isoformat() + 'T23:59:59Z'
        events_result = self.service.events().list(
            calendarId=self.vacation_calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime',
        ).execute()
        events = events_result.get('items', [])

        if events:
            for event in events:
                start_str = event['start'].get(
                    'dateTime',
                    event['start'].get('date'),
                )
                start_date = datetime.fromisoformat(
                    start_str.split('T')[0],
                ).date()
                days_off[start_date] = event['summary']
        else:
            logger.info('No upcoming events found.')
        if vacation:
            logger.info(f'Found the following vacations: {vacation}')
        else:
            logger.info('No vacation were Found')
        return days_off

    # Not used, proven unrealiable like "faire le pont" and we might work
    # during public holidays better add it to the vacation calendar manually
    def list_holidays(self, period: Period) -> DaysOff:
        if self.holiday_calendar_ids is None:
            raise ValueError('No holiday calendar ID provided')
        time_min = period.start.isoformat() + 'T00:00:00Z'
        time_max = period.end.isoformat() + 'T23:59:59Z'
        holiday_dict: DaysOff = {}

        for calendar_id in self.holiday_calendar_ids:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime',
            ).execute()
            events = events_result.get('items', [])

            if not events:
                logger.info('No events found.')
                return []

            for event in events:
                start = event['start'].get('date')
                holiday_name = event['summary']
                holiday_date = datetime.strptime(start, "%Y-%m-%d").date()
                holiday_dict[holiday_date] = holiday_name

        return holiday_dict
