#!/usr/bin/env python

from PyPDF2 import PdfFileReader


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
import sys, os

try:
    with open('attachments/loaded.json') as F:
        loaded_messages = json.load(F)
except:
    loaded_messages = {}

try:
    with open('attachments/decryption_password.json', 'r') as F:
        decryption_pw = json.load(F)['password']
except:
    decryption_pw = input('Enter decryption password: ')
    with open('attachments/decryption_password.json', 'w') as F:
        json.dump({'password': decryption_pw}, F)

cur_msg = 0
for messageId in loaded_messages.keys():
    loaded_messages[messageId]['texts'] = {}
    for filename in loaded_messages[messageId]['files']:
        texts = []
        with open(filename, 'rb') as F:
            # pdf = PdfFileReader(F)
            # if pdf.decrypt('') == 0:
            #     pdf.decrypt(decryption_pw)
            # info = pdf.getDocumentInfo()
            # number_of_pages = pdf.getNumPages()

            # page = pdf.getPage(0)
            # print(page)
            # print('Page type: {}'.format(str(type(page))))

            # text = page.extractText()
            # print(text)

            # Open a PDF file.
            fp = open(filename, 'rb')

            # Create a PDF parser object associated with the file object.
            parser = PDFParser(fp)

            # Create a PDF document object that stores the document structure.
            # Password for initialization as 2nd parameter
            try:
                document = PDFDocument(parser, password='')
            except:
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
        
        # now use texts to extract data
        loaded_messages[messageId]['texts'][filename] = list(map(lambda t: {"text": t.get_text(), "bbox": t.bbox, "page": t.page_number}, texts))
    print ("Finished [{}/{}]: {}".format(cur_msg, len(loaded_messages), messageId))
    cur_msg += 1

with open('attachments/loaded.json', 'w') as F:
    json.dump(loaded_messages, F)