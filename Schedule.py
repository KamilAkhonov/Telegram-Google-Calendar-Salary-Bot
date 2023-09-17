from __future__ import print_function
import datetime
import os.path
import sys
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def extract_numbers(input_string):
    # Use a regular expression to find all the numbers in the string
    numbers = re.findall(r'\d+', input_string)
    # Combine the found numbers into one line
    result = ''.join(numbers)
    return result


if len(sys.argv) != 2:
    print("Ошибка: необходимо передать один аргумент.")
    sys.exit(1)

# Get the value of the argument (variable) from the command line
try:
    flag = int(sys.argv[1])
except ValueError:
    print("Ошибка: аргумент должен быть числом.")
    sys.exit(1)

if datetime.datetime.utcnow().day < 15 or datetime.datetime.utcnow().day >= 30:
    if flag == 1:
        # 30th of the previous month
        start_date = datetime.datetime(datetime.datetime.utcnow().year, datetime.datetime.utcnow().month - 1, 30)
        # 14th of the current month (not including)
        end_date = datetime.datetime(datetime.datetime.utcnow().year, datetime.datetime.utcnow().month, 15)
    elif flag == 0:
        # 15th of the current month
        start_date = datetime.datetime(datetime.datetime.utcnow().year, datetime.datetime.utcnow().month - 1, 15)
        # 30th of the current month (not including)
        end_date = datetime.datetime(datetime.datetime.utcnow().year, datetime.datetime.utcnow().month - 1, 30)
else:
    if flag == 0:
        # 30th of the previous month
        start_date = datetime.datetime(datetime.datetime.utcnow().year, datetime.datetime.utcnow().month - 1, 30)
        # 14th of the current month (not including)
        end_date = datetime.datetime(datetime.datetime.utcnow().year, datetime.datetime.utcnow().month, 15)
    elif flag == 1:
        # 15th of the current month
        start_date = datetime.datetime(datetime.datetime.utcnow().year, datetime.datetime.utcnow().month, 15)
        # 30th of the current month (not including)
        end_date = datetime.datetime(datetime.datetime.utcnow().year, datetime.datetime.utcnow().month, 30)

salary = []
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


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
        start_date_utc = start_date.isoformat() + 'Z'
        end_date_utc = end_date.isoformat() + 'Z'
        # Request events in the specified date range
        events_result = service.events().list(calendarId=' ',
                                              timeMin=start_date_utc,
                                              timeMax=end_date_utc,
                                              singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            print('No events found in the specified range.')
        else:
            for event in events:
                try:
                    event_name_as_int = int(extract_numbers(event['summary']))
                    salary.append(event_name_as_int)
                except ValueError:
                    # If it cannot be converted to a number, skip the event
                    pass
        print(sum(salary))
    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()
