#!/usr/bin/env python

from extraction.qnb import QNBAccountsSummaryDocument, QNBCreditCardDocument
from visualization import Plotter

import json
import os, sys
from functools import reduce

if __name__ == "__main__":
    try:
        with open('attachments/loaded.json') as F:
            loaded_messages = json.load(F)
    except:
        loaded_messages = {}

    documents = []
    for messageId in loaded_messages.keys():
        for filename in loaded_messages[messageId]['texts'].keys():
            if "ACCOUNT STATEMENT" in filename:
                documents.append(QNBAccountsSummaryDocument(filename, loaded_messages[messageId]['texts'][filename]))
            elif "CREDIT CARD STATEMENT" in filename:
                documents.append(QNBCreditCardDocument(filename, loaded_messages[messageId]['texts'][filename]))
            else:
                continue
            
            if not documents[-1].validate():
                print ("{} is invalid".format(documents[-1].filename))
                print (documents[-1].dump(lines=False, tables=True))
                raise Exception("Parsing failure!")
            else:
                print ("{} is good".format(documents[-1].filename))
                
    Plotter.plot(reduce(lambda a, b: a + b, map(lambda doc: doc.ledgers, documents), []))
    
    with open('attachments/loaded.json', 'w') as F:
        json.dump(loaded_messages, F)