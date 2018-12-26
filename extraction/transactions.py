import datetime

class Transaction(object):
    def __init__(self, date, delta, desc):
        self.date = date
        self.delta = delta
        self.desc = desc
