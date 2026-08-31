import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']
TOKEN_FILE = os.path.join(os.path.dirname(__file__), '..', 'token.json')
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')


def get_credentials():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f'credentials.json not found at {CREDENTIALS_FILE}. '
                    'Download OAuth 2.0 Client ID from Google Cloud Console.'
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=8080, open_browser=False)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds


def get_drive_service():
    creds = get_credentials()
    return build('drive', 'v3', credentials=creds)


def upload_pdf(file_path, filename, folder_id=None):
    service = get_drive_service()

    file_metadata = {
        'name': filename,
        'mimeType': 'application/pdf',
    }
    if folder_id:
        file_metadata['parents'] = [folder_id]

    media = MediaFileUpload(file_path, mimetype='application/pdf', resumable=True)

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()

    file_id = file.get('id')

    service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    return {
        'file_id': file_id,
        'url': file.get('webViewLink')
    }


def delete_file(file_id):
    try:
        service = get_drive_service()
        service.files().delete(fileId=file_id).execute()
        return True
    except Exception:
        return False


def replace_file(old_file_id, file_path, filename, folder_id=None):
    delete_file(old_file_id)
    return upload_pdf(file_path, filename, folder_id)
