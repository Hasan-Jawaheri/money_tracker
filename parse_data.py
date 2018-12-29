#!/usr/bin/env python

from extraction import BANK_UTILITIES
from visualization import Plotter

import json
import os, sys
from functools import reduce

if __name__ == "__main__":
    try:
        with open('attachments/loaded_statements.json') as F:
            loaded_statements = json.load(F)
    except:
        loaded_statements = {}
    
    documents = []
    for message_id in loaded_statements.keys():
        for filename in loaded_statements[message_id]['texts'].keys():
            doc = BANK_UTILITIES[loaded_statements[message_id]["bank"]].createDocument(filename, loaded_statements[message_id]['texts'][filename])
            if doc == None:
                print ("Cannot identify document: {}".format(filename))
                continue

            print ("Loaded {} as {}".format(filename, str(doc)))
            documents.append(doc)
                
    Plotter.plot(reduce(lambda a, b: a + b, map(lambda doc: doc.ledgers, documents), []))
    
    with open('attachments/loaded_statements.json', 'w') as F:
        json.dump(loaded_statements, F)