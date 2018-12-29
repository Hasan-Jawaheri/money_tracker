from extraction.qnb import QNBUtilities

UTILITY_CLASSES = [
    QNBUtilities,
]

BANK_UTILITIES = {}
for bank_utility in UTILITY_CLASSES:
    BANK_UTILITIES[bank_utility.NAME] = bank_utility
