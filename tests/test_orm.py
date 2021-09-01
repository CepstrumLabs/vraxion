import sqlite3

import pytest

from vraxion.api import Api
from vraxion.orm import Database, Table

def test_assert_can_create_database(database):
    
    assert isinstance(database.connection, sqlite3.Connection)
    assert database.tables == []


def test_create_table(database):
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
    assert Book.published.sql_type == "INTEGER"
    assert Book.title.sql_type == "TEXT"

def test_create_tables(database, Author, Book):
    
    database.create(Author)
    database.create(Book)

    assert Author._get_create_sql() == "CREATE TABLE IF NOT EXISTS author (id INTEGER PRIMARY KEY AUTOINCREMENT, age INTEGER, name TEXT);"
    assert Book._get_create_sql() == "CREATE TABLE IF NOT EXISTS book (id INTEGER PRIMARY KEY AUTOINCREMENT, author_id INTEGER, published INTEGER, title TEXT);"
    for table in ("author", "book"):
        assert table in database.tables
