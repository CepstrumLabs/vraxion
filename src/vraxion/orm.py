import sqlite3
import inspect

class Table:

    @classmethod
    def _get_create_sql(cls):
        fields = [
            "id INTEGER PRIMARY KEY AUTOINCREMENT",
        ]
        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                 fields.append(f"{name} {field.sql_type}")
            elif isinstance(field, ForeignKey):
                fields.append(f"{name}_id INTEGER")
        
        fields = ", ".join(fields)
        name = cls.__name__.lower()
        CREATE_TABLE_SQL = "CREATE TABLE IF NOT EXISTS {name} ({fields});"
        return CREATE_TABLE_SQL.format(name=name, fields=fields)

class Column:
    def __init__(self, type):
        self.type = type

    @property
    def sql_type(self):
        PY_TO_SQL_TYPE_MAP = {
            int: "INTEGER",
            float: "REAL",
            str: "TEXT",
            bytes: "BLOB",
            bool: "INTEGER",  # 0 or 1
        }
        return PY_TO_SQL_TYPE_MAP[self.type]

class ForeignKey:
    def __init__(self, table):
        self.table = table

class ManyToMany(Column):
    pass


class Database:

    def __init__(self, path):
        self.path = path
        self.connection = sqlite3.Connection(self.path)

    def create(self, table: Table):
        create_sql = table._get_create_sql()
        self.connection.execute(create_sql)

    @property
    def tables(self):
        GET_TABLES_SQL = "SELECT name FROM sqlite_master WHERE type = 'table';"
        return [table[0] for table in self.connection.execute(GET_TABLES_SQL).fetchall()]