#!/usr/bin/env python

from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import os
import base64
import json

try:
    with open('attachments/loaded_statements.json') as F:
        loaded_statements = json.load(F)
except:
    loaded_statements = {}

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
    cur_msg = 0
    for message in messages:
        cur_msg += 1
        if message['id'] in loaded_statements:
            print ("[{}/{}]: [{}] Already downloaded".format(cur_msg, len(messages), message['id']))
            continue
        try:
            print ("[{}/{}]: [{}] downloading...".format(cur_msg, len(messages), message['id']))
            message = service.users().messages().get(userId='me', id=message['id']).execute()
            new_loaded_message = {'files': []}
            part_num = 0
            for part in message['payload']['parts']:
                part_num += 1
                print ("  [{}/{}]".format(part_num, len(message['payload']['parts'])))
                if 'parts' in part:
                    for part in part['parts']:
                        if 'filename' in part and len(part['filename']) > 0:
                            print ("    {}".format(part['filename']))
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
                            new_loaded_message.append(path)
            loaded_statements[message['id']] = new_loaded_message
        except Exception as e:
            print ('An error occurred: %s' % e)

with open('attachments/loaded_statements.json', 'w') as F:
    json.dump(loaded_statements, F)

