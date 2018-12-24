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

class Document(object):
    def __init__(self, filename, texts_json):
        self.filename = filename
        self.texts = self.fixTexts(texts_json)
        self.lines = self.buildLines()
    
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

    def dump(self):
        dump = "[{}]".format(self.filename)
        for line in self.lines:
            dump += "\n> {}".format(line.dump())
        return dump

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
                print (documents[-1].dump())
                asd = asdd
        
    # with open('attachments/loaded.json', 'w') as F:
    #     json.dump(loaded_messages, F)