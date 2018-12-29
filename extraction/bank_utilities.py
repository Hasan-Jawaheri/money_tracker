import pkgutil
import inspect
import extraction

BANK_UTILITY_CLASSES = []
for importer, modname, ispkg in pkgutil.iter_modules(extraction.__path__):
    if ispkg:
        module = __import__("extraction." + modname, fromlist="dummy")
        for attr in map(lambda attr: getattr(module, attr), dir(module)):
            if inspect.isclass(attr) and issubclass(attr, extraction.BankUtilityInterface):
                BANK_UTILITY_CLASSES.append(attr)

BANK_UTILITIES = {}
for bank_utility in BANK_UTILITY_CLASSES:
    BANK_UTILITIES[bank_utility.NAME] = bank_utility
