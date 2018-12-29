#!/usr/bin/env python

from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import os
import base64
import json

class GMailFetcher:
    SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
    SERVICE = None

    def initializeService(store='token.json', credentials='credentials.json'):
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        store = file.Storage(store)
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(credentials, GMailFetcher.SCOPES)
            creds = tools.run_flow(flow, store)
        GMailFetcher.SERVICE = build('gmail', 'v1', http=creds.authorize(Http()))
    
    def fetchEmails(query):
        if not GMailFetcher.SERVICE:
            GMailFetcher.initializeService()

        results = GMailFetcher.SERVICE.users().messages().list(userId='me', q=query).execute()
        return list(map(lambda message: message['id'], results.get('messages', [])))
    
    def downloadAllAttachments(message_id, folder='attachments'):
        if not GMailFetcher.SERVICE:
            GMailFetcher.initializeService()

        message = GMailFetcher.SERVICE.users().messages().get(userId='me', id=message_id).execute()
        new_loaded_message = {'files': []}
        loaded_file_paths = []
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
                            attachment = GMailFetcher.SERVICE.users().messages().attachments().get(userId='me', id=attachmentId, messageId=message_id).execute()
                        file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                        path = os.path.join(folder, message_id + '_' + part['filename'])
                        f = open(path, 'wb')
                        f.write(file_data)
                        f.close()
                        loaded_file_paths.append(path)
        return loaded_file_paths

if __name__ == "__main__":
    try:
        with open('attachments/loaded_statements.json') as F:
            loaded_statements = json.load(F)
    except:
        loaded_statements = {}

    message_ids = GMailFetcher.fetchEmails('qnb statement')

    cur_msg = 0
    for message_id in message_ids:
        cur_msg += 1
        if message_id in loaded_statements:
            print ("[{}/{}]: [{}] Already downloaded".format(cur_msg, len(message_ids), message_id))
            continue
        try:
            print ("[{}/{}]: [{}] downloading...".format(cur_msg, len(message_ids), message_id))
            loaded_statements[message_id] = {"files": GMailFetcher.downloadAllAttachments(message_id)}
        except Exception as e:
            print ('An error occurred: %s' % e)

    with open('attachments/loaded_statements.json', 'w') as F:
        json.dump(loaded_statements, F)

