#!/usr/bin/env python

from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import os
import base64
import json

try:
    with open('attachments/loaded.json') as F:
        loaded_messages = json.load(F)
except:
    loaded_messages = {}

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'

# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('gmail', 'v1', http=creds.authorize(Http()))

# Call the Gmail API
results = service.users().messages().list(userId='me', q='qnb statement').execute()
messages = results.get('messages', [])

if not messages:
    print('No messages found.')
else:
    for message in messages:
        if message['id'] in loaded_messages:
            continue
        try:
            message = service.users().messages().get(userId='me', id=message['id']).execute()
            for part in message['payload']['parts']:
                if 'parts' in part:
                    for part in part['parts']:
                        if 'filename' in part and len(part['filename']) > 0:
                            attachment = None
                            attachmentId = part['body']['attachmentId']
                            if 'data' in part['body']:
                                attachment = part['body']
                            else:
                                attachment = service.users().messages().attachments().get(userId='me', id=attachmentId, messageId=message['id']).execute()
                            file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                            path = os.path.join('attachments', message['id'] + '_' + part['filename'])
                            f = open(path, 'wb')
                            f.write(file_data)
                            f.close()
                            if message['id'] not in loaded_messages:
                                loaded_messages[message['id']] = {'files': []}
                            loaded_messages[message['id']]['files'].append(path)
        except Exception as e:
            print ('An error occurred: %s' % e)

with open('attachments/loaded.json', 'w') as F:
    json.dump(loaded_messages, F)

