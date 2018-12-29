#!/usr/bin/env python

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
import pdfminer
import json

def extractTextsFromPFFFile(filename, decryption_pw=''):
    texts = []
    with open(filename, 'rb') as F:
        # Open a PDF file.
        fp = open(filename, 'rb')

        # Create a PDF parser object associated with the file object.
        parser = PDFParser(fp)

        # Create a PDF document object that stores the document structure.
        # Password for initialization as 2nd parameter
        try:
            document = PDFDocument(parser, password='')
        except:
            if decryption_pw != '':
                document = PDFDocument(parser, password=decryption_pw)

        # Check if the document allows text extraction. If not, abort.
        # if not document.is_extractable:
        #     raise PDFTextExtractionNotAllowed

        # Create a PDF resource manager object that stores shared resources.
        rsrcmgr = PDFResourceManager()

        # Create a PDF device object.
        device = PDFDevice(rsrcmgr)

        # BEGIN LAYOUT ANALYSIS
        # Set parameters for analysis.
        laparams = LAParams()

        # Create a PDF page aggregator object.
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)

        # Create a PDF interpreter object.
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        def parse_obj(lt_objs, page):

            # loop over the object list
            for obj in lt_objs:
                obj.page_number = page
                # if it's a textbox, print text and location
                if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
                    texts.append(obj)
                    # print ("%6d, %6d, %s" % (obj.bbox[0], obj.bbox[1], obj.get_text().replace('\n', '_')))
                    # print(obj.bbox)

                # if it's a container, recurse
                elif isinstance(obj, pdfminer.layout.LTFigure):
                    parse_obj(obj._objs, page)

        # loop over all pages in the document
        page_num = 1
        for page in PDFPage.create_pages(document):

            # read the page into a layout object
            interpreter.process_page(page)
            layout = device.get_result()

            # extract text from this object
            parse_obj(layout._objs, page_num)
            page_num += 1

    return texts

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

