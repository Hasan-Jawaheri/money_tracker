from extraction.qnb.documents import QNBDocument
from extraction.qnb.tables import QNBAccountTypeTable, QNBAccountSummaryTable
from extraction.ledgers import Ledger

class QNBAccountsSummaryDocument(QNBDocument):
    def validate(self):
        if len(self.tables) % 2 != 0 or len(self.tables) == 0:
            return False
        
        self.ledgers = []
        for i in range(0, len(self.tables), 2):
            t1 = self.tables[i]
            t2 = self.tables[i+1]

            if not isinstance(t1, QNBAccountTypeTable) or not isinstance(t2, QNBAccountSummaryTable):
                return False
            if not t1.validate() or not t2.validate():
                return False

            if len(t2.transactions) > 0:
                self.ledgers.append(Ledger(self, name=t1.account_type.string, opening_balance=t2.opening_balance, transactions=t2.transactions))
        
        return True
