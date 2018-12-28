import datetime
import json

class Transaction(object):
    def __init__(self, date, delta, desc, ledger=None, document=None):
        self.date = date
        self.delta = delta
        self.desc = desc
        self.document = document if document is not None else (ledger.documents[0] if ledger and len(ledger.documents) > 0 else None)
        self.ledger = ledger
    
    def toJSON(self):
        return {
            "date": self.date.isoformat(),
            "delta": self.delta,
            "desc": self.desc,
            "filename": self.document.filename if self.document else ""
        }

