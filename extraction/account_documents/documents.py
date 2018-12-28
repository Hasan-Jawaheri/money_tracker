from extraction.tables import Table
from extraction.hardcoded_filters.text_filters import TextFilters
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
    def __init__(self, filename, texts_json):
        self.filename = filename
        self.texts = self.fixTexts(json.loads(json.dumps(texts_json)))
        self.lines = self.buildLines()
        self.tables = self.parseTables()
        self.ledgers = []
    
    def fixTexts(self, texts):
        new_texts = []
        for i in range(0, len(texts)):
            bbox = texts[i]['bbox']
            bbox[1] = 1000 - bbox[1]
            bbox[3] = 1000 - bbox[3]
            splitted_texts = texts[i]['text'].strip().split('\n')
            num_lines = len(splitted_texts)
            if num_lines > 1 and '' in splitted_texts:
                raise("Unhandled exception")
            elif num_lines == 1 and splitted_texts[0] == "":
                continue
            line_height = abs(bbox[3] - bbox[1]) / len(splitted_texts)
            max_line_len = max(map(lambda t: len(t), splitted_texts))
            for j in range(num_lines):
                new_text = json.loads(json.dumps(texts[i]))
                new_text['text'] = splitted_texts[num_lines-1-j]
                new_text['bbox'] = [bbox[0], (bbox[1] - line_height*j), bbox[0] + (bbox[2]-bbox[0]) * (len(new_text['text'])/max_line_len), (bbox[1] - line_height*(j-1))]
                new_texts += TextFilters.textSplitter(json.loads(json.dumps(new_text)))
        new_texts.sort(key=lambda t: t['page'] * 2000 + t['bbox'][1])
        return list(map(lambda T: Text(T), new_texts))
    
    def buildLines(self):
        line_texts = [[]]
        for text in self.texts:
            if len(line_texts[-1]) > 0 and (text.y > line_texts[-1][0].y + 7 or text.page > line_texts[-1][0].page):
                line_texts.append([])
            line_texts[-1].append(text)
            
        return list(filter(lambda line: TextFilters.lineFilter(line), map(lambda texts: Line(texts), line_texts)))
    
    def parseTables(self):
        return list(filter(lambda t: t is not None, map(lambda i: Table.findInLines(self.lines[i:]), range(len(self.lines)))))

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