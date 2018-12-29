#!/usr/bin/env python

from extraction import BANK_UTILITIES
from email_fetchers import EMAIL_FETCHERS
import json

if __name__ == "__main__":
    try:
        with open('attachments/loaded_statements.json') as F:
            loaded_statements = json.load(F)
    except:
        loaded_statements = {}

    SELECTED_BANK = "QNB"
    SELECTED_MAIL_CLIENT = "GMAIL"

    EMAIL_FETCHER = EMAIL_FETCHERS[SELECTED_MAIL_CLIENT]
    BANK_UTILITY = BANK_UTILITIES[SELECTED_BANK]

    message_ids = EMAIL_FETCHER.fetchEmails(BANK_UTILITY.EMAIL_SEARCH_QUERY)

    cur_msg = 0
    for message_id in message_ids:
        cur_msg += 1
        if message_id in loaded_statements:
            print ("[{}/{}]: [{}] Already downloaded".format(cur_msg, len(message_ids), message_id))
            continue
        try:
            print ("[{}/{}]: [{}] downloading...".format(cur_msg, len(message_ids), message_id))
            loaded_statements[message_id] = {"bank": BANK_UTILITY.NAME, "files": EMAIL_FETCHER.downloadAllAttachments(message_id)}
        except Exception as e:
            print ('An error occurred: %s' % e)

    with open('attachments/loaded_statements.json', 'w') as F:
        json.dump(loaded_statements, F)

