from extraction.tables import Table, Row
from extraction.transactions import Transaction
import re
import datetime
import copy

class QNBCreditCardTable(Table):
    @staticmethod
    def parseFromLines(lines):
        return Table.parseFromLines(lines, ["post date", "purchase date", "description & reference", "foreign currency", "amount in qar"], QNBCreditCardTable)
        
    def __init__(self, template_line, rows):
        super().__init__(template_line, rows)
        self.opening_balance = 0
        self.closing_balance = 0
        self.transactions = []
        self.validate()
    
    def trimRows(self):
        for i in range(len(self.rows)):
            if self.rows[i]['description & reference'] == None or self.rows[i]['amount in qar'] == None:
                self.rows = self.rows[:i]
                return
    
    def validate(self):
        self.transactions = []
        if len(self.rows) < 1:
            return False
        
        if self.rows[0]['description & reference'].string != 'PREVIOUS STATEMENT\'S CLOSING BALANCE':
            return False

        try:
            self.opening_balance = float(self.rows[0]['amount in qar'].string[:-3].replace(',', '')) * (-1 if self.rows[0]['amount in qar'].string[-2:] == 'DB' else 1)
        except Exception as e:
            print(1, e)
            return False
        
        self.closing_balance = self.opening_balance
        for row in self.rows[1:]:
            try:
                m = re.match("([0-9]+)/([0-9]+)/([0-9]+)", row['purchase date'].string)
                date = datetime.datetime(int(m.groups()[2]), int(m.groups()[1]), int(m.groups()[0]))
                self.transactions.append(Transaction(date=date, delta=float(row['amount in qar'].string[:-3].replace(',', '')) * (-1 if row['amount in qar'].string[-2:] == 'DB' else 1), desc=row['description & reference'].string))
                self.closing_balance += self.transactions[-1].delta
            except Exception as e:
                print (2, e)
                print (row['purchase date'], row['amount in qar'], row.attributes['post date'].string)
                return False

        return True

    