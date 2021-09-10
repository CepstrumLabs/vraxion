import sqlite3
import inspect
import logging

logger = logging.getLogger("vraxion.orm")

class Table:

    def __getattribute__(self, key: str):
        _data = super().__getattribute__("_data")
        if key in _data:
            return _data[key]
        return super().__getattribute__(key)

    def __setattr__(self, key: str, value):
        super().__setattr__(key, value)
        if key in self._data:
            self._data[key] = value

    def __init__(self, **kwargs):
        self._data = {"id": None}
        for key, value in kwargs.items():
                self._data[key] = value

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

    @classmethod
    def _get_columns(cls):
        columns = []
        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                columns.append(f"{name}")
            elif isinstance(field, ForeignKey):
                columns.append(f"{name}_id")
        return columns

    def _get_insert_sql(self):
        cls = self.__class__
        INSERT_SQL = "INSERT INTO {name} ({columns}) VALUES ({placeholders});"
        fields = []
        placeholders = []
        values = []
        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append(name)
                values.append(getattr(self, name))
                placeholders.append("?")
            elif isinstance(field, ForeignKey):
                fields.append(name + "_id")
                values.append(getattr(self, name).id)
                placeholders.append("?")
        columns = ", ".join(self._get_columns())
        placeholders =  ", ".join(placeholders)
        sql = INSERT_SQL.format(name=cls.__name__.lower(), columns=columns, placeholders=placeholders)
        return sql, values

    @classmethod
    def _get_select_all_sql(cls):
        columns = ["id"]
        columns.extend(cls._get_columns())
        name = cls.__name__.lower()
        SELECT_ALL_SQL = "SELECT {columns} FROM {name};" 
        return SELECT_ALL_SQL.format(columns=', '.join(columns), name=name), columns

    @classmethod
    def _get_select_sql(cls, id):
        columns = ["id"]
        columns.extend(cls._get_columns())
        SELECT_ALL_SQL = "SELECT {columns} FROM {name} WHERE (id=?);"
        params = [id]
        return SELECT_ALL_SQL.format(columns=', '.join(columns), name=cls.__name__.lower()), columns, params

    def _get_update_sql(self):
        cls = self.__class__
        tbl_name = cls.__name__.lower()
        fields = []
        values = []
        UPDATE_SQL = "UPDATE {name} SET {fields} WHERE id = ?;"
        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append(name)
                values.append(getattr(self, name))
            elif isinstance(field, ForeignKey):
                fields.append(name + "_id")
                values.append(getattr(self, name).id)
        values.append(getattr(self, "id"))
        return (UPDATE_SQL.format(name=tbl_name, fields=", ".join([f"{field} = ?" for field in fields])), values)

    def _get_delete_sql(self):
        cls = self.__class__
        DELETE_SQL = "DELETE FROM {name} where id = ?;"
        id = getattr(self, "id")
        values = [id]
        return DELETE_SQL.format(name=cls.__name__.lower()), values

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
        logger.info(f"Create table with sql {create_sql}")

    def save(self, instance: Table):
        sql, params = instance._get_insert_sql()
        try:
            logger.info(f"cursor = self.connection.execute({sql}, {params})")
            cursor = self.connection.execute(sql, params)
        except Exception:
            logger.exception(f"Encountered exception with query sql {sql} and params {params}")
        instance._data["id"] = cursor.lastrowid
        self.connection.commit()

    def all(self, table: Table):
        select_all_sql, fields = table._get_select_all_sql()
        cursor = self.connection.execute(select_all_sql)
        rows = cursor.fetchall()
        instances = []
        for row in rows:
            instance = table()
            for field, value in zip(fields, row):
                setattr(instance, field, value)
            instances.append(instance)
        return instances

    def get(self, table: Table, id: int):
        sql, fields, params = table._get_select_sql(id=id)
        row = self.connection.execute(sql, params).fetchone()
        if row is None:
            raise Exception(f"{table.__name__} instance with id {id} does not exist")
        instance = table()
        for field, value in zip(fields, row):
            if field.endswith("_id"):
                field = field[:-3]
                fk = getattr(table, field)
                value = self.get(fk.table, id=value)
            setattr(instance, field, value)
        return instance

    def update(self, instance):
        update_sql, values = instance._get_update_sql()
        self.connection.execute(update_sql, values)
        self.connection.commit()

    def delete(self, instance):
        delete_sql, values = instance._get_delete_sql()
        self.connection.execute(delete_sql, values)
        self.connection.commit()

    @property
    def tables(self):
        GET_TABLES_SQL = "SELECT name FROM sqlite_master WHERE type = 'table';"
        return [table[0] for table in self.connection.execute(GET_TABLES_SQL).fetchall()]