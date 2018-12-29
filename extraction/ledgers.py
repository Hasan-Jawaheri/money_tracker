from extraction.transactions import Transaction
from functools import reduce
import re
import json

class Ledger(object):
    def __init__(self, document, name, opening_balance, transactions, start_date=None):
        if isinstance(document, list):
            self.documents = document
        else:
            self.documents = [document]
        self.name = name
        self.transactions = transactions
        self.opening_balance = opening_balance
        self.closing_balance = self.opening_balance + reduce(lambda a, b: a + b, map(lambda t: t.delta, self.transactions), 0)
        if start_date is None:
            self.start_date = transactions[0].date
        else:
            self.start_date = start_date
        for tx in transactions:
            tx.ledger = self
    
    def mergeWith(self, ledger):
        remove_clutter_regex = re.compile('[^a-zA-Z0-9]')

        new_transactions = []
        for tx in ledger.transactions:
            duplicate = False
            for dup_tx in self.transactions:
                if remove_clutter_regex.sub('', tx.desc) == remove_clutter_regex.sub('', dup_tx.desc) and tx.date == dup_tx.date:
                    if abs(tx.delta - dup_tx.delta) > 0.1:
                        raise Exception("Duplicate transaction with different value!\n{}\n{}/{}  {}/{}".format(tx.desc, tx.delta, dup_tx.delta, tx.date, dup_tx.date))
                    duplicate = dup_tx
                    break
            if not duplicate:
                new_transactions.append(Transaction(date=tx.date, delta=tx.delta, desc=tx.desc, ledger=self, document=ledger.documents[0]))
        self.transactions += new_transactions
        self.transactions.sort(key=lambda tx: tx.date)
        self.closing_balance = self.opening_balance + reduce(lambda a, b: a + b, map(lambda t: t.delta, self.transactions), 0)
        self.documents += ledger.documents
    
    def dump(self):
        return("[{}][{}][{} -> {}] {} transactions in {}".format(self.name, self.start_date, self.opening_balance, self.closing_balance, len(self.transactions), list(map(lambda doc: doc.filename, self.documents))))
    
    def toJSON(self):
        return {
            "documents": list(map(lambda doc: doc.filename, self.documents)),
            "name": self.name,
            "transactions": list(map(lambda tx: tx.toJSON(), self.transactions)),
            "opening_balance": self.opening_balance,
            "closing_balance": self.closing_balance,
            "start_date": self.start_date.isoformat(),
        }
