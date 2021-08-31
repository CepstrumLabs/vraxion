import sqlite3

import pytest

from vraxion.api import Api
from vraxion.orm import Database, Table

def test_assert_can_create_database():
    database = Database("./test.db")
    
    assert isinstance(database.connection, sqlite3.Connection)
    assert database.tables == []


def test_create_table():
    database = Database("./test.db")   
    assert isinstance(database.connection, sqlite3.Connection)
    assert database.tables == [] 

def test_define_tables(Author, Book):
    assert Author.name.type == str
    assert Author.age.type == int
    assert Book.author.table == Author
    assert Book.published.type == bool
    assert Book.title.type == str

    assert Author.name.sql_type == "TEXT"
    assert Author.age.sql_type == "INTEGER"
    assert Book.published.sql_type == "BOOLEAN"
    assert Book.title.sql_type == "TEXT"

