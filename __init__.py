from __future__ import print_function
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.parse import extract_datetime
import pickle
import os.path
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import httplib2
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
#from oauth2client.tools import run
from oauth2client import tools


# SCOPES for google calendar API.
SCOPES = ['https://www.googleapis.com/auth/calendar']
# OAuth2webserverFlow for Google People API
FLOW = OAuth2WebServerFlow(
    client_id='361001423406-meqq5djv2vf54fhd0ect7163ugkpssmm.apps.googleusercontent.com',
    client_secret='pioORdrpsd-cFemxkETi08yM',
    scope='https://www.googleapis.com/auth/contacts.readonly',
    user_agent='Focus Smart Box')


class CreateEvent(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_handler(IntentBuilder("").require("querry"))
    def handle_create_event(self):

        # Getting the credentials for G.People API
        storage = Storage('info.dat')
        credentials = storage.get()
        if credentials is None or credentials.invalid is True:
            credentials = tools.run_flow(FLOW, storage)

        http = httplib2.Http()
        http = credentials.authorize(http)

        people_service = build(serviceName='people', version='v1', http=http)

        results = people_service.people().connections().list(
            resourceName='people/me',
            pageSize=10,
            personFields='emailAddresses,names').execute()
        connections = results.get('connections', [])

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
        reservation = self.get_response('do you need to make a reservation for a meeting room? Yes or No?')
        if reservation == 'yes':
            r = self.get_response('which Room do you want to make a reservation for? ')
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
            # needs to be verified !!!!!!!
            room = ""

        mr = {'email': room}
        start = self.get_response('when does it start?')
        end = self.get_response('when does it end?')
        st = extract_datetime(start)
        et = extract_datetime(end)
        invitation = self.get_response('would you like to invite an other employees to this meeting? Yes or No?')
        if invitation == 'yes':
            # getting the attendees
            atto = []
            noms = []
            f = 0
            i = 1
            g = 0
            found = False
            found2 = False
            attendees = ['blabla@blabla'] * maxattendees
            for person in connections:
                emailAddresses = person.get('emailAddresses', [])
                names = person.get('names', [])
                atto.append(emailAddresses[0].get('value'))
                noms.append(names[0].get('displayName'))
            p = len(noms)
            # first attendee
            a = self.get_response('who do you want to invite first?')
            if a != '':
                while (g != p) & (found is False):
                    # if the name in the input matches the a name in the list we add the email of that person to the
                    # attendees list which will be treated later to delete the examples 'blabla@blabla.com'
                    if noms[g] == a:
                        attendees[0] = atto[g]
                        g = g + 1
                        found = True
                    else:
                        g = g + 1
                if found is False:
                    print('contact not found try again please')
            else:
                print('no attendees added')
            # other attendees to add less then max
            while i != maxattendees:
                a = input()
                if a == '':
                    break
                else:
                    while (f != p) | (found2 is False):
                        if noms[f] == a:
                            attendees[i] = atto[f]
                            found2 = True
                        f = f + 1
                i = i + 1
            # until this stage we have a list of attendees + blanks filled with blabla@blabla.om
            # print(attendees)
            l = len(attendees)
            # print(l)
            # in this part we are going to get the attendees without the blanks
            t = 0
            att = []
            while t != l:
                if attendees[t] != 'blabla@blabla':
                    att.append(attendees[t])
                    t = t + 1
                else:
                    t = t + 1
            l2 = len(att)
            # print(att)
            # print(l2)

            attendee = []
            for r in range(l2):
                email = {'email': att[r]}
                attendee.append(email)
            attendee.append(mr)

        # Add an event
        event = {
            'summary': title,
            'location': r,
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
            'attendees': attendee,
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
