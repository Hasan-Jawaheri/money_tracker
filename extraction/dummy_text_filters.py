
class DummyTextFilters:
    @staticmethod
    def textSplitter(text):
        return [text]
    
    @staticmethod
    def lineFilter(line):
        return True
