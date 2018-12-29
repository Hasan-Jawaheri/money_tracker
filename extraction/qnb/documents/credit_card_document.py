from extraction.qnb.documents import QNBDocument
from extraction.qnb.tables import QNBCreditCardTable, QNBCreditCardTypeTable, QNBCreditCardSummaryTable
from extraction.ledgers import Ledger

class QNBCreditCardDocument(QNBDocument):
    def validate(self):
        if len(self.tables) != 3:
            return False
        
        t1 = self.tables[0]
        t2 = self.tables[1]
        t3 = self.tables[2]

        if not isinstance(t1, QNBCreditCardSummaryTable) or not isinstance(t2, QNBCreditCardTypeTable) or not isinstance(t3, QNBCreditCardTable):
            return False
        if not t1.validate() or not t2.validate() or not t3.validate():
            return False
        if abs(t1.closing_balance - t3.closing_balance) > 0.1:
            return False
        
        if len(t3.transactions) > 0:
            self.ledgers = [Ledger(self, name="CREDIT CARD", opening_balance=t3.opening_balance, transactions=t3.transactions)]
        else:
            self.ledgers = []
    
        return True
