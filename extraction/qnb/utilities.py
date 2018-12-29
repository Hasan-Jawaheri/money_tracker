from extraction import Document, Table
import inspect

class QNBUtilities:
    NAME = "QNB"
    EMAIL_SEARCH_QUERY = "qnb statement"

    @staticmethod
    def createDocument(filename, texts):
        import extraction.qnb.documents as qnb_documents
        DOCUMENT_TYPES = filter(lambda attr: inspect.isclass(attr) and issubclass(attr, Document) and attr != Document, map(lambda module_attr: getattr(qnb_documents, module_attr), dir(qnb_documents)))

        for DT in DOCUMENT_TYPES:
            doc = DT(filename, texts)
            if doc.validate():
                return doc

        return None

    @staticmethod
    def findTableInLines(lines):
        import extraction.qnb.tables as qnb_account_tables
        TABLE_TYPES = filter(lambda attr: inspect.isclass(attr) and issubclass(attr, Table) and attr != Table, map(lambda module_attr: getattr(qnb_account_tables, module_attr), dir(qnb_account_tables)))

        for TT in TABLE_TYPES:
            table = TT.parseFromLines(lines)
            if table is not None:
                return table
        return None
