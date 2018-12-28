import datetime
import json

class Transaction(object):
    def __init__(self, date, delta, desc, ledger=None):
        self.date = date
        self.delta = delta
        self.desc = desc
        self.ledger = ledger
    
    def toJSON(self):
        return {
            "date": self.date.isoformat(),
            "delta": self.delta,
            "desc": self.desc,
        }

