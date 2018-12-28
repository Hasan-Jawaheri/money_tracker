from extraction.ledger import Ledger
from functools import reduce

class Plotter:
    @staticmethod
    def plot(ledgers):
        account_to_ledgers = {}
        account_to_ledger = {}
        for ledger in ledgers:
            if ledger.name not in account_to_ledgers:
                account_to_ledgers[ledger.name] = [ledger]
            else:
                account_to_ledgers[ledger.name].append(ledger)
        
        account_to_combined_ledger = {}
        for account_name in account_to_ledgers.keys():
            opening_balance = None
            opening_date = None
            for ledger in account_to_ledgers[account_name]:
                if not opening_date or opening_date > ledger.transactions[0].date:
                    opening_balance = ledger.opening_balance
                    opening_date = ledger.start_date
            combined_ledger = Ledger([], account_name, opening_balance, [], start_date=opening_date)
            for ledger in account_to_ledgers[account_name]:
                combined_ledger.mergeWith(ledger)

            account_to_combined_ledger[account_name] = combined_ledger
            print ("{}".format(combined_ledger.dump()))
            