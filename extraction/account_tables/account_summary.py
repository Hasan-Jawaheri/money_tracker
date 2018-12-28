from extraction.tables import Table, Row
from extraction.transactions import Transaction
import re
import datetime
import copy

class AccountSummaryTable(Table):
    @staticmethod
    def parseFromLines(lines):
        return Table.parseFromLines(lines, ["date", "description", "debit", "credit", "balance"], AccountSummaryTable)
        
    def __init__(self, template_line, rows):
        super().__init__(template_line, rows)
        self.opening_balance = 0
        self.closing_balance = 0
        self.transactions = []
        self.mergeDescriptionRows()
        self.validate()
    
    # rows that are only description should merge with the row before
    def mergeDescriptionRows(self):
        if len(self.rows) >= 3 and self.rows[0].description.string.lower() == "opening balance" and self.rows[1].description != None and len(list(filter(lambda col: col is not None, self.rows[1].field_texts))) == 1 and len(list(filter(lambda col: col is not None, self.rows[2].field_texts))) >= 4:
            # special case: "Opening balance" sometimes merges with what's below it incorrectly...
            self.rows[2].description = copy.deepcopy(self.rows[2].description)
            self.rows[2].description.string = self.rows[1].description.string + "\n" + self.rows[2].description.string
            del self.rows[1]
        for r in reversed(range(len(self.rows))):
            if r > 0 and self.rows[r].description != None and len(list(filter(lambda col: col is not None, self.rows[r].field_texts))) == 1:
                self.rows[r-1].description = copy.deepcopy(self.rows[r-1].description)
                self.rows[r-1].description.string += "\n" + self.rows[r].description.string
                del self.rows[r]
    
    def validate(self):
        self.transactions = []
        if len(self.rows) < 2:
            return False

        try:
            self.opening_balance = float(self.rows[0].balance.string.replace(',', ''))
            self.closing_balance = float(self.rows[-1].balance.string.replace(',', ''))
        except Exception as e:
            return False
        
        cur_balance = self.opening_balance
        for row in self.rows:
            if row.date is not None:
                try:
                    m = re.match("([0-9]+)/([0-9]+)/([0-9]+)", row.date.string)
                    date = datetime.datetime(int(m.groups()[2]), int(m.groups()[1]), int(m.groups()[0]))
                    if row.debit is not None:
                        self.transactions.append(Transaction(date=date, delta=float(row.debit.string.replace(',', '')), desc=row.description.string))
                        cur_balance += self.transactions[-1].delta
                    if row.credit is not None:
                        self.transactions.append(Transaction(date=date, delta=float(row.credit.string.replace(',', '')), desc=row.description.string))
                        cur_balance += self.transactions[-1].delta
                except Exception as e:
                    print (e)
                    return False
        
        if abs(cur_balance - self.closing_balance) > 0.1:
            return False

        return True

