from extraction.documents import Document
from extraction.account_tables import AccountTypeTable, DebitCardTable

class AccountsSummaryDocument(Document):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debit_tables = []
        self.credit_tables = []

    def validate(self):
        self.debit_tables = []
        self.credit_tables = []
        if len(self.tables) % 2 != 0 or len(self.tables) == 0:
            return False
        
        for i in range(0, len(self.tables), 2):
            t1 = self.tables[i]
            t2 = self.tables[i+1]

            if not isinstance(t1, AccountTypeTable) or not isinstance(t2, DebitCardTable):
                return False
        
        return True
