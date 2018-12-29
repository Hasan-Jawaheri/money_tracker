from extraction.tables import Table, Row
import re
import datetime
import copy

class QNBCreditCardTypeTable(Table):
    @staticmethod
    def parseFromLines(lines):
        return Table.parseFromLines(lines, ["card number", "card holder", "credit limit", "payment due", "due date"], QNBCreditCardTypeTable)
        
    def __init__(self, template_line, rows):
        super().__init__(template_line, rows)
        self.mergeCardNumberRows()
        self.validate()
    
    # rows that are only iban should merge with the row before
    def mergeCardNumberRows(self):
        for r in reversed(range(len(self.rows))):
            if r > 0 and self.rows[r]['card number'] != None and len(list(filter(lambda col: col is not None, self.rows[r].field_texts))) == 1:
                self.rows[r-1].attributes['card number'] = copy.deepcopy(self.rows[r-1]['card number'])
                self.rows[r-1]['card number'].string += "\n" + self.rows[r]['card number'].string
                del self.rows[r]
    
    def validate(self):
        if len(self.rows) != 1:
            return False
        
        if not self.rows[0]['card number'] or not self.rows[0]['card holder'] or not self.rows[0]['credit limit'] or not self.rows[0]['payment due'] or not self.rows[0]['due date']:
            return False

        return True

