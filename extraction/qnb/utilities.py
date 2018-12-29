from extraction import Table
import inspect

def findTableInLines(lines):
    import extraction.qnb.tables as qnb_account_tables
    TABLE_TYPES = filter(lambda attr: inspect.isclass(attr) and issubclass(attr, Table) and attr != Table, map(lambda module_attr: getattr(qnb_account_tables, module_attr), dir(qnb_account_tables)))

    for TT in TABLE_TYPES:
        table = TT.parseFromLines(lines)
        if table is not None:
            return table
    return None