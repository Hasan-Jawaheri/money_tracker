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
    rects = []
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
    
        # Adds extra properties to the obj (e.g. font size and name)
        def obj_add_properties(obj):
            obj.fontname = ""
            obj.fontsize = 0
            for o in obj._objs:
                if isinstance(o,pdfminer.layout.LTTextLine):
                    for c in  o._objs:
                        if isinstance(c, pdfminer.layout.LTChar):
                            obj.fontname = c.fontname
                            obj.fontsize = c.size
            return obj

        def parse_obj(lt_objs, page):
            # loop over the object list
            for obj in lt_objs:
                obj.page_number = page
                # if it's a textbox, print text and location
                if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
                    texts.append(obj_add_properties(obj))
                elif isinstance(obj, pdfminer.layout.LTRect):
                    rects.append(obj)
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

    return texts, rects
