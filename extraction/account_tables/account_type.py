from extraction.tables import Table, Row
import re
import datetime
import copy

class AccountTypeTable(Table):
    @staticmethod
    def parseFromLines(lines):
        return Table.parseFromLines(lines, ["account (iban)", "currency", "account type"], AccountTypeTable)
        
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
            return False
        
        if not self.rows[0]['account (iban)'] or not self.rows[0]['currency'] or not self.rows[0]['account type']:
            return False

        return True

