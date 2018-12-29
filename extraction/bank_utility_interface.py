
class BankUtilityInterface:
    NAME = "<Unknown>"
    EMAIL_SEARCH_QUERY = None

    @staticmethod
    def createDocument(filename, texts, rects):
        raise Exception("Unimplemented")

    @staticmethod
    def findTableInLines(lines):
        raise Exception("Unimplemented")
