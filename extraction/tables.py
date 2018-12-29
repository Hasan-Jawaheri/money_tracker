
class Field(object):
    def __init__(self, text_from, alignment):
        self.text_from = text_from
        self.string = text_from.string
        self.alignment = alignment

class Row(object):
    @staticmethod
    def fromLine(template_line, line):
        if len(line.texts) > 0:
            potential_texts = list(line.texts) # make a copy so modifying this list doesn't influence line.texts
            fields = [None]*(len(template_line.texts))
            for text in potential_texts:
                lowest_dist = 100000
                closest_text = None
                closest_index = -1
                for i in range(len(fields)):
                    prev_template_text = template_line.texts[i-1] if i > 0 else None
                    cur_template_text = template_line.texts[i]
                    next_template_text = template_line.texts[i+1] if i < len(fields)-1 else None
                    dist = abs((text.x1 + text.x)/2 - (cur_template_text.x + cur_template_text.x1)/2)
                    within_bounds = (not prev_template_text or text.x > prev_template_text.x1-4) and (not next_template_text or text.x1 < next_template_text.x+4)
                    some_overlap = (text.x <= cur_template_text.x and text.x1 >= cur_template_text.x) or (text.x <= cur_template_text.x1 and text.x1 >= cur_template_text.x1) or (text.x >= cur_template_text.x and text.x1 <= cur_template_text.x1)
                    if dist < lowest_dist and within_bounds and some_overlap:
                        lowest_dist = dist
                        closest_text = text
                        closest_index = i
                if closest_text != None and fields[closest_index] == None:
                    fields[closest_index] = Field(closest_text, "center")
                else:
                    return None

            return Row(template_line, fields, line)
        return None

    def __init__(self, template_line, field_texts, line_from):
        assert(len(template_line.texts) == len(field_texts))
        self.template_line = template_line
        self.line_from = line_from
        self.field_texts = field_texts
        self.attributes = dict(list(map(lambda i: (template_line.texts[i].string.lower(), field_texts[i]), range(len(template_line.texts)))))
    
    def __getattr__(self, name):
        return self.attributes[name]
    def __getitem__(self, key):
        if isinstance(key, str):
            return self.attributes[key]
        return self.field_texts[key]

class Table(object):
    @staticmethod
    def parseFromLines(lines, template, account_type):
        if len(lines) > 0:
            if list(map(lambda t: t.string.lower(), lines[0].texts)) == template:
                template = lines[0]
                rows = []
                for line in lines[1:]:
                    row = Row.fromLine(template, line)
                    if row is None:
                        break
                    rows.append(row)
                if len(rows) > 0:
                    return account_type(template, rows)
        return None

    @staticmethod
    def findInLines(lines):
        import extraction.qnb.tables as qnb_account_tables
        TABLE_TYPES = [
            qnb_account_tables.QNBAccountSummaryTable,
            qnb_account_tables.QNBAccountTypeTable,
            qnb_account_tables.QNBCreditCardTable,
            qnb_account_tables.QNBCreditCardTypeTable,
            qnb_account_tables.QNBCreditCardSummaryTable
        ]

        for TT in TABLE_TYPES:
            table = TT.parseFromLines(lines)
            if table is not None:
                return table
        return None
    
    def __init__(self, template_line, rows):
        self.template_line = template_line
        self.rows = rows
        self.trimRows()
    
    def validate(self):
        return True
    
    def trimRows(self):
        pass
    
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
                    extra_lines = "".join(list(map(lambda line: "\n{}{}".format(" " * (sum(column_text_lengths[0:col])), line), text.split('\n')[1:])))
                    text = text[:text.find('\n')]
                dump += "{}{}".format(text, " " * (column_text_lengths[col] - len(text)))
            dump += extra_lines + "\n"
        return dump.strip()
