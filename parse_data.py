#!/usr/bin/env python

from extraction.documents import Document

import json
import os, sys


if __name__ == "__main__":
    try:
        with open('attachments/loaded.json') as F:
            loaded_messages = json.load(F)
    except:
        loaded_messages = {}

    documents = []
    for messageId in loaded_messages.keys():
        for filename in loaded_messages[messageId]['texts'].keys():
            documents.append(Document(filename, loaded_messages[messageId]['texts'][filename]))
            if "ACCOUNT STATEMENT" in documents[-1].filename:
                if len(documents[-1].tables) > 0 and not documents[-1].tables[0].validate():
                    print ("{} is invalid".format(documents[-1].filename))
                    print (documents[-1].dump(lines=True, tables=True))
                    raise Exception("Parsing failure!")
                elif len(documents[-1].tables) > 0:
                    print ("{} is good".format(documents[-1].filename))
                else:
                    print ("{} has no tables!".format(documents[-1].filename))
                    print (documents[-1].dump(lines=True, tables=False))
                    raise Exception("Parsing failure!")
        
    with open('attachments/loaded.json', 'w') as F:
        json.dump(loaded_messages, F)