#!/usr/bin/env python

import json
import os, sys

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
        return "{}  <{}-{}>".format(list(map(lambda T: str(T), self.texts)), int(self.y), int(self.y1))

class Table(object):
    class Row(object):
        @staticmethod
        def fromLine(template_line, line):
            if len(line.texts) > 0:
                potential_texts = list(line.texts) # make a copy so modifying this list doesn't influence line.texts
                fields = [None]*(len(template_line.texts))
                for i in range(len(fields)):
                    for text in potential_texts:
                        # check left, right and center aligns
                        if text.x >= template_line.texts[i].x - 4 and (i == (len(fields)-1) or text.x1 < template_line.texts[i+1].x) or\
                           text.x1 <= template_line.texts[i].x1 + 4 and (i == 0 or text.x > template_line.texts[i-1].x1) or\
                           False: # (text.x >= template_line.texts[i].x and text.x1 <= template_line.texts[i].x1) or (text.x <) center align (tricky?)
                            fields[i] = text
                            potential_texts.remove(text)

                if len(potential_texts) == 0:
                    return Table.Row(template_line, fields)
            return None

        def __init__(self, template_line, field_texts):
            assert(len(template_line.texts) == len(field_texts))
            self.template_line = template_line
            self.field_texts = field_texts
            self.attributes = dict(list(map(lambda i: (template_line.texts[i].string.lower(), field_texts[i]), range(len(template_line.texts)))))
        
        def __getattr__(self, name):
            return self.attributes[name]
        def __getitem__(self, key):
            return self.field_texts[key]

    @staticmethod
    def parseFromLines(lines):
        TABLE_TYPES = [
            DebitCardTable,
        ]

        for TT in TABLE_TYPES:
            table = TT.parseFromLines(lines)
            if table is not None:
                return table
        return None
    
    def __init__(self, template_line, rows):
        self.template_line = template_line
        self.rows = rows
    
    def dump(self):
        len_no_nl = lambda s: len(s) if '\n' not in s else max(map(lambda ss: len(ss), s.split("\n")))
        column_text_lengths = \
            list(map(lambda col:
                max(
                    [len_no_nl(self.template_line.texts[col].string)] +
                    list(map(lambda row: len_no_nl(row[col].string) if row[col] is not None else 0, self.rows))
                ) + 4,
                range(len(self.template_line.texts))
            ))
        rows_texts = [list(map(lambda t: t.string, self.template_line.texts))] + list(map(
            lambda row: list(map(lambda t: t.string if t is not None else "", row.field_texts)),
            self.rows
        ))

        dump = ""
        for row_texts in rows_texts:
            extra_lines = ""
            for col in range(len(row_texts)):
                text = row_texts[col]
                if '\n' in text:
                    extra_lines = "\n" + "".join(list(map(lambda line: "{}{}\n".format(" " * (sum(column_text_lengths[0:col])), line), text.split('\n')[1:])))
                    text = text[:text.find('\n')]
                dump += "{}{}".format(text, " " * (column_text_lengths[col] - len(text)))
            dump += extra_lines + "\n\n"
        return dump

class DebitCardTable(Table):
    @staticmethod
    def parseFromLines(lines):
        if len(lines) > 0:
            if list(map(lambda t: t.string.lower(), lines[0].texts)) == ["date", "description", "debit", "credit", "balance"]:
                template = lines[0]
                rows = []
                for line in lines[1:]:
                    row = Table.Row.fromLine(template, line)
                    if row is None:
                        break
                    rows.append(row)
                if len(rows) > 0:
                    return DebitCardTable(template, rows)
        return None
        
    def __init__(self, template_line, rows):
        super().__init__(template_line, rows)
        self.mergeDescriptionRows()
    
    # rows that are only description should merge with the row before
    def mergeDescriptionRows(self):
        for r in reversed(range(len(self.rows))):
            if r > 0 and self.rows[r].description != None and len(list(filter(lambda col: col is not None, self.rows[r].field_texts))) == 1:
                self.rows[r-1].description.string += "\n" + self.rows[r].description.string
                del self.rows[r]

class Document(object):
    def __init__(self, filename, texts_json):
        self.filename = filename
        self.texts = self.fixTexts(texts_json)
        self.lines = self.buildLines()
        self.tables = self.parseTables()
    
    def fixTexts(self, texts):
        new_texts = []
        for i in range(0, len(texts)):
            bbox = texts[i]['bbox']
            bbox[1] = 1000 - bbox[1]
            bbox[3] = 1000 - bbox[3]
            splitted_texts = texts[i]['text'].strip().split('\n')
            line_height = abs(bbox[3] - bbox[1]) / len(splitted_texts)
            num_lines = len(splitted_texts)
            for j in range(num_lines):
                new_text = json.loads(json.dumps(texts[i]))
                new_text['text'] = splitted_texts[num_lines-1-j]
                new_text['bbox'] = [bbox[0], (bbox[1] - line_height*j), bbox[2], (bbox[1] - line_height*(j-1))]
                new_texts.append(json.loads(json.dumps(new_text)))
        new_texts.sort(key=lambda t: t['page'] * 2000 + t['bbox'][1])
        return list(map(lambda T: Text(T), new_texts))
    
    def buildLines(self):
        line_texts = [[]]
        for text in self.texts:
            if len(line_texts[-1]) > 0 and text.y > line_texts[-1][0].y + 7:
                line_texts.append([])
            line_texts[-1].append(text)
            
        return list(map(lambda texts: Line(texts), line_texts))
    
    def parseTables(self):
        return list(filter(lambda t: t is not None, map(lambda i: Table.parseFromLines(self.lines[i:]), range(len(self.lines)))))

    def dump(self, lines=True, tables=True):
        dumps = []

        if lines:
            dump = "[{}]".format(self.filename)
            for line in self.lines:
                dump += "\n> {}".format(line.dump())
            dumps.append(dump)

        if tables:
            dumps.append("\n".join(list(map(lambda T: T.dump(), self.tables))))

        return "\n".join(dumps)

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
                print (documents[-1].dump(lines=False, tables=True))
                asd = asdd
        
    with open('attachments/loaded.json', 'w') as F:
        json.dump(loaded_messages, F)