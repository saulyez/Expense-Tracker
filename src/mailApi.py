import os
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle


class GmailHandler:
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    def __init__(self, creds_file='mail_creds.json', token_file='mail_token.pickle'):
        self.creds_file = creds_file
        self.token_file = token_file
        self.service = self.authenticate()

    def authenticate(self):
        creds = None
        # Load existing credentials from the token file
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)

        # If credentials are invalid or missing, refresh or reauthorize
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())  # Attempt to refresh the token
                except Exception as e:
                    print(f"Failed to refresh token: {e}")
                    print("Reauthorization required.")
                    creds = None  # Force reauthorization
            if not creds:  # If no valid credentials, trigger reauthorization
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.creds_file,
                        self.SCOPES
                    )
                    # Explicitly specify offline access
                    creds = flow.run_local_server(port=0, access_type='offline')
                except Exception as e:
                    raise Exception(f"An error occurred during the authorization flow: {e}")

            # Save the new credentials to the token file
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)

        # Build the Gmail API service object
        return build('gmail', 'v1', credentials=creds)

    def get_attachments(self, subject='expenses', save_dir='attachments'):
        """
        Fetch and save attachments from Gmail messages matching the query.
        """
        query = f'subject:{subject} has:attachment'
        os.makedirs(save_dir, exist_ok=True)  # Ensure save directory exists

        try:
            results = self.service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
        except Exception as e:
            print(f"An error occurred while fetching messages: {e}")
            return

        if not messages:
            print('No messages found.')
            return

        for message in messages:
            try:
                msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
                payload = msg.get('payload', {})

                for part in payload.get('parts', []):
                    if part.get('filename'):
                        filename = part['filename']
                        attachment_id = part['body'].get('attachmentId')
                        if attachment_id:
                            attachment = self.service.users().messages().attachments().get(
                                userId='me', messageId=message['id'], id=attachment_id
                            ).execute()
                            data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))

                            save_path = os.path.join(save_dir, filename)
                            with open(save_path, 'wb') as f:
                                f.write(data)
                                print(f'File "{filename}" saved to "{save_path}"')

            except Exception as e:
                print(f"An error occurred while processing message {message['id']}: {e}")
