from extraction.tables import Table, Row
import re
import datetime
import copy

class CreditCardSummaryTable(Table):
    @staticmethod
    def parseFromLines(lines):
        return Table.parseFromLines(lines, ["card number", "card holder", "purchases", "cash", "credits &", "closing balance"], CreditCardSummaryTable)
        
    def __init__(self, template_line, rows):
        super().__init__(template_line, rows)
        self.closing_balance = 0
        self.mergeCardNumberRows()
        self.validate()
    
    def trimRows(self):
        if len(self.rows) > 0 and self.rows[0]['cash'] is not None and self.rows[0]['cash'].string == 'Withdrawals':
            self.rows = self.rows[1:]
        if len(self.rows) > 1:
            self.rows = self.rows[:1]
    
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
        
        if not self.rows[0]['card number'] or not self.rows[0]['card holder'] or not self.rows[0]['purchases'] or not self.rows[0]['cash'] or not self.rows[0]['credits &'] or not self.rows[0]['closing balance']:
            return False
        
        try:
            self.closing_balance = float(self.rows[0]['closing balance'].string[:-3].replace(',', '')) * (-1 if self.rows[0]['closing balance'].string[-2:] == 'DB' else 1)
        except Exception as e:
            print(1, e)
            return False

        return True

