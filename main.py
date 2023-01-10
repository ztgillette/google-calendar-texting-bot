from __future__ import print_function

import datetime
from datetime import date
import os.path

from info import *

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from multiprocessing import context
from email.message import EmailMessage
import ssl
import smtplib

CARRIERS = {
    "att": "@mms.att.net",
    "tmobile": "@tmomail.net",
    "verizon": "@vtext.com",
    "sprint": "@messaging.sprintpcs.com"
}

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def sendMessage(e):

    #set up message
    message = "Good Morning, Katarina!!\nToday you have:\n\n"

    if(len(e) == 0):
        message += "Nothing on the calendar!!\n"
    else:
        for ev in e:
            message += ev
            message += '\n'

    message += "\nLove,\nZach"

    #security
    context = ssl.create_default_context()

    #send text
    recipient = phone_number + CARRIERS[carrier]
    auth = (EMAIL, PASSWORD)
    
    #connect to Gmail
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(auth[0], auth[1])
    
    #send text
    server.sendmail(auth[0], recipient, message)

    print("text sent")

    # close the smtp server
    server.close()
    

def getMyEvents(day, events):
    if not events:
        return(["No Events!"])

    # Prints the start and name of the next 10 events
    l = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        #print(start, event['summary'])
        if(str(start)[:10] == day):
            answer = event['summary'] + calcEventTime(start)
            l.append(answer)
    return l

def calcEventTime(t):
    hours = t[11:13]
    minute = t[14:16]
    hour = int(hours)

    am = True

    if(hour >= 12):
        am = False
        hour %= 12

    if(am):
        www = "AM"
    else:
        www = "PM"

    answer = " @" + str(hour) + ":" + minute + " " + www
    return answer

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
        #print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        #my code
        #return only events that are occuring during inputted day
        d = date.today()
        e = getMyEvents(d, events)

        #print events in terminal
        print("Hello, Katarina!!")
        print("Here are your events for today:")
        for ev in e:
            print(ev)

        #send texts
        sendMessage(e)

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()