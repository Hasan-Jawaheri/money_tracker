from extraction.account_documents import Document
from extraction.account_tables import CreditCardTable, CreditCardTypeTable, CreditCardSummaryTable

class CreditCardDocument(Document):
    def validate(self):
        if len(self.tables) != 3:
            return False
        
        t1 = self.tables[0]
        t2 = self.tables[1]
        t3 = self.tables[2]

        if not isinstance(t1, CreditCardSummaryTable) or not isinstance(t2, CreditCardTypeTable) or not isinstance(t3, CreditCardTable):
            return False
        if not t1.validate() or not t2.validate() or not t3.validate():
            return False
        if abs(t1.closing_balance - t3.closing_balance) > 0.1:
            return False
    
        return True
