from extraction.documents import Text, Line, Document
from extraction.tables import Table
from extraction.qnb.filters import QNBTextFilters
import json

class QNBDocument(Document):
    def __init__(self, filename, texts_json):
        super().__init__(filename, texts_json, text_filters=QNBTextFilters)
        
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
                new_texts += self.text_filters.textSplitter(json.loads(json.dumps(new_text)))
        new_texts.sort(key=lambda t: t['page'] * 2000 + t['bbox'][1])
        return list(map(lambda T: Text(T), new_texts))
    