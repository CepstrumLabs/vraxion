import sqlite3


PY_TO_SQL_TYPE_MAP = {
    str: "TEXT",
    int: "INTEGER",
    bool: "BOOLEAN"
}

class Table:

    def __init__(self, name):
        self.name = name
    
    _columns = []
    _rows = []


class Column:
    def __init__(self, type):
        self.type = type
        self.sql_type = PY_TO_SQL_TYPE_MAP[type]

class ForeignKey:
    def __init__(self, table):
        self.table = table

class ManyToMany(Column):
    pass


class Database:

    def __init__(self, path):
        self.path = path
        self.connection = sqlite3.Connection(self.path)

    def create_table(self, table: Table):
        pass

    @property
    def tables(self):
        return []