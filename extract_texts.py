#!/usr/bin/env python

from extraction import extractTextsFromPFFFile
import json

if __name__ == "__main__":
    try:
        with open('attachments/loaded_statements.json') as F:
            loaded_statements = json.load(F)
    except:
        loaded_statements = {}

    try:
        with open('attachments/decryption_password.json', 'r') as F:
            decryption_pw = json.load(F)['password']
    except:
        decryption_pw = input('Enter decryption password: ')
        with open('attachments/decryption_password.json', 'w') as F:
            json.dump({'password': decryption_pw}, F)

    cur_msg = 1
    for id in loaded_statements.keys():
        if not 'texts' in loaded_statements[id]:
            loaded_statements[id]['texts'] = {}
            for filename in loaded_statements[id]['files']:
                texts = extractTextsFromPFFFile(filename, decryption_pw=decryption_pw)
                # now use texts to extract data
                loaded_statements[id]['texts'][filename] = list(map(lambda t: {"text": t.get_text(), "bbox": t.bbox, "page": t.page_number}, texts))
                print ("Extracted file {}".format(filename))
            print ("Extracted PDF contents [{}/{}]: {}".format(cur_msg, len(loaded_statements), id))
        else:
            print ("Already extracted [{}/{}]: {}".format(cur_msg, len(loaded_statements), id))
        cur_msg += 1

    with open('attachments/loaded_statements.json', 'w') as F:
        json.dump(loaded_statements, F)

