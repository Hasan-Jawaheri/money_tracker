from extraction.documents import Document
from extraction.account_tables import CreditCardTable, CreditCardTypeTable

class CreditCardDocument(Document):
    def validate(self):
        if len(self.tables) % 2 != 0 or len(self.tables) == 0:
            return False
            
        for i in range(0, len(self.tables), 2):
            t1 = self.tables[i]
            t2 = self.tables[i+1]

            if not isinstance(t1, CreditCardTypeTable) or not isinstance(t2, CreditCardTable):
                return False
        
        return True
