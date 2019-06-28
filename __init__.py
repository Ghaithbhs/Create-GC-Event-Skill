from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.parse import extract_datetime
from __future__ import print_function
from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']


class CreateEvent(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_handler(IntentBuilder("").require("querry"))
    def handle_create_event(self):
        # Get credentials for google calendar with smart.box@focus-corporation.com
        # and token management
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)
        # Getting information about the event
        title = self.get_response('what\'s the name of the new event')
        description = self.get_response('can you tell me more about it ?')
        location = self.get_response('what\'s the location of the event')
        reservation = self.get_response('do you need to make a reservation for a meeting room? Yes or No?')
        if reservation == 'yes':
            r = self.get_response('which Romm do you want to make a reservation for? ')
            maxattendees = 10
            if r == "Midoun meeting room":
                room = "focus-corporation.com_3436373433373035363932@resource.calendar.google.com"
            elif r == "Aiguilles Meeting Room":
                room = "focus-corporation.com_3132323634363237333835@resource.calendar.google.com"
            elif r == "Barrouta Meeting Room":
                room = "focus-corporation.com_3335353934333838383834@resource.calendar.google.com"
            elif r == "Kantaoui Meeting Room":
                room = "focus-corporation.com_3335343331353831343533@resource.calendar.google.com"
            elif r == "Gorges Meeting Room":
                room = "focus-corporation.com_3436383331343336343130@resource.calendar.google.com"
            elif r == "Ichkeul Meeting Room":
                room = "focus-corporation.com_36323631393136363531@resource.calendar.google.com"
            elif r == "Khemir Meeting Room":
                room = "focus-corporation.com_3935343631343936373336@resource.calendar.google.com"
            elif r == "Tamaghza Meeting Room":
                room = "focus-corporation.com_3739333735323735393039@resource.calendar.google.com"
            elif r == "Friguia Meeting Room":
                room = "focus-corporation.com_3132343934363632383933@resource.calendar.google.com"
                maxattendees = 15
            elif r == "Ksour Meeting Room":
                room = "focus-corporation.com_@resource.calendar.google.com"
            elif r == "Medeina Meeting Room":
                room = "focus-corporation.com_@resource.calendar.google.com"
            elif r == "Thyna Meeting Room":
                room = "focus-corporation.com_@resource.calendar.google.com"
        else:
            room = ""
        start = self.get_response('when does it start')
        end = self.get_response('when does it end')
        st = extract_datetime(start)
        et = extract_datetime(end)
        # Add an event
        event = {
            'summary': title,
            'location': location,
            'description': description,
            'start': {
                'dateTime': st,
                'timeZone': 'Tunisia/Tunis',
            },
            'end': {
                'dateTime': et,
                'timeZone': 'Tunisia/Tunis',
            },
            'recurrence': [
                'RRULE:FREQ=DAILY;COUNT=2'
            ],
            'attendees': [
                {
                 'email': room
                 },
            ],
            'maxAttendees': maxattendees,
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        event = service.events().insert(calendarId='primary', sendNotifications=True, body=event).execute()
        print
        'Event created: %s' % (event.get('htmlLink'))
        self.speak_dialog('eventAdded')


def create_skill():
    return CreateEvent()
