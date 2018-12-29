from extraction.tables import Table
from extraction.dummy_text_filters import DummyTextFilters
import json

class Text(object):
    def __init__(self, json_obj):
        self.string = json_obj['text']
        self.x = json_obj['bbox'][0]
        self.y = json_obj['bbox'][1]
        self.x1 = json_obj['bbox'][2]
        self.y1 = json_obj['bbox'][3]
        self.width = self.x1 - self.x
        self.height = self.y1 - self.y
        self.page = json_obj['page']
    
    def __unicode__(self):
        return self.string

    def __str__(self):
        return self.string

class Line(object):
    def __init__(self, texts):
        self.texts = sorted(texts, key=lambda t: t.x)
        self.y = self.texts[0].y
        self.y1 = self.texts[0].y1
        self.height = self.texts[0].height
    
    def dump(self):
        return "{}  <height {}-{}> <widths {}>".format(list(map(lambda T: str(T), self.texts)), int(self.y), int(self.y1), ",".join(list(map(lambda T: "{}-{}".format(int(T.x), int(T.x1)), self.texts))))

class Document(object):
    def __init__(self, filename, texts_json, text_filters=DummyTextFilters):
        self.filename = filename
        self.text_filters = text_filters
        self.texts = self.fixTexts(json.loads(json.dumps(texts_json)))
        self.lines = self.buildLines()
        self.tables = self.parseTables()
        self.ledgers = []
    
    def fixTexts(self, texts):
        return list(map(lambda T: Text(T), texts))
    
    def buildLines(self):
        line_texts = [[]]
        for text in self.texts:
            if len(line_texts[-1]) > 0 and (text.y > line_texts[-1][0].y + 7 or text.page > line_texts[-1][0].page):
                line_texts.append([])
            line_texts[-1].append(text)
            
        return list(filter(lambda line: self.text_filters.lineFilter(line), map(lambda texts: Line(texts), line_texts)))
    
    def parseTables(self):
        return list(filter(lambda t: t is not None, map(lambda i: Table.findInLines(self.lines[i:]), range(len(self.lines)))))
    
    def validate(self):
        return True

    def dump(self, lines=True, tables=True):
        dumps = []

        if lines:
            dump = "[{}]".format(self.filename)
            for line in self.lines:
                dump += "\n> {}".format(line.dump())
            dumps.append(dump)

        if tables:
            dumps.append("\n\n".join(list(map(lambda T: T.dump(), self.tables))))

        return "\n\n".join(dumps)