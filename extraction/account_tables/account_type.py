from extraction.tables import Table, Row
import re
import datetime
import copy

class AccountTypeTable(Table):
    @staticmethod
    def parseFromLines(lines):
        if len(lines) > 0:
            if list(map(lambda t: t.string.lower(), lines[0].texts)) == ["account (iban)", "currency", "account type"]:
                template = lines[0]
                rows = []
                for line in lines[1:]:
                    row = Row.fromLine(template, line)
                    if row is None:
                        break
                    rows.append(row)
                if len(rows) > 0:
                    return AccountTypeTable(template, rows)
        return None
        
    def __init__(self, template_line, rows):
        super().__init__(template_line, rows)
        self.mergeIBANRows()
        self.validate()
    
    # rows that are only iban should merge with the row before
    def mergeIBANRows(self):
        for r in reversed(range(len(self.rows))):
            if r > 0 and self.rows[r]['account (iban)'] != None and len(list(filter(lambda col: col is not None, self.rows[r].field_texts))) == 1:
                self.rows[r-1].attributes['account (iban)'] = copy.deepcopy(self.rows[r-1]['account (iban)'])
                self.rows[r-1]['account (iban)'].string += "\n" + self.rows[r]['account (iban)'].string
                del self.rows[r]
    
    def validate(self):
        if len(self.rows) != 1:
            print(len(self.rows))
            return False
        
        if not self.rows[0]['account (iban)'] or not self.rows[0]['currency'] or not self.rows[0]['account type']:
            print(self.rows[0]['account (iban)'], self.rows[0]['currency'], self.rows[0]['account type'])
            return False

        return True

