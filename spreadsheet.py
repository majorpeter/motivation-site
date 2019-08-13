import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery


_SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def _fetch_credentials():
    """
    based on https://developers.google.com/sheets/api/quickstart/python
    :return: a credentials object to be used with discovery.build
    """
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
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', _SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def fetch_cells_from_sheet(sheet_id, range):
    """
    download a range of cells from spreadsheets
    :param sheet_id: ID part of the spreadsheet URL
    :param range: part of a row or column, e.g. A1:A10
    :return: list of cell values as string
    """
    sheet_service = discovery.build('sheets', 'v4', credentials=_fetch_credentials()).spreadsheets()
    result = sheet_service.values().get(spreadsheetId=sheet_id, range=range, valueRenderOption='UNFORMATTED_VALUE',
                                        dateTimeRenderOption='FORMATTED_STRING').execute()
    return result['values']
