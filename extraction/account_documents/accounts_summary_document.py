from extraction.account_documents import Document
from extraction.account_tables import AccountTypeTable, AccountSummaryTable
from extraction.ledger import Ledger

class AccountsSummaryDocument(Document):
    def validate(self):
        if len(self.tables) % 2 != 0 or len(self.tables) == 0:
            return False
        
        self.ledgers = []
        for i in range(0, len(self.tables), 2):
            t1 = self.tables[i]
            t2 = self.tables[i+1]

            if not isinstance(t1, AccountTypeTable) or not isinstance(t2, AccountSummaryTable):
                return False
            if not t1.validate() or not t2.validate():
                return False

            if len(t2.transactions) > 0:
                self.ledgers.append(Ledger(self, name=t1.account_type.string, opening_balance=t2.opening_balance, transactions=t2.transactions))
        
        return True
