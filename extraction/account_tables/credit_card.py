from extraction.tables import Table, Row
import re
import datetime
import copy

class CreditCardTable(Table):
    @staticmethod
    def parseFromLines(lines):
        return Table.parseFromLines(lines, ["post date", "purchase date description & reference", "foreign currency", "amount in qar"], CreditCardTable)
        
    def __init__(self, template_line, rows):
        super().__init__(template_line, rows)
        self.validate()

