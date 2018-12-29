import copy

class QNBTextFilters:
    TEXT_TO_SPLIT = {
        "Purchase Date Description & Reference": ["Purchase Date", "Description & Reference"]
    }

    @staticmethod
    def textSplitter(text):
        if text['text'] in QNBTextFilters.TEXT_TO_SPLIT:
            new_strings = QNBTextFilters.TEXT_TO_SPLIT[text['text']]
            new_texts = []
            sizes = list(map(lambda s: len(s) / len(text['text']), new_strings))
            original_text_width = text['bbox'][2] - text['bbox'][0]
            cur_pos = 0
            for (string, size) in zip(new_strings, sizes):
                new_texts.append(copy.deepcopy(text))
                new_texts[-1]['text'] = string
                new_texts[-1]['bbox'][0] = text['bbox'][0] + cur_pos
                cur_pos += original_text_width * size
                new_texts[-1]['bbox'][2] = text['bbox'][0] + cur_pos
            return new_texts
        return [text]
    
    @staticmethod
    def lineFilter(line):
        return line.y > 300 and line.y1 < 970 # header and footer
