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

def test_create_instance(database, Author):
    database.create(Author)

    michael = Author(name="Michael", age=31)

    assert michael.name == "Michael"
    assert michael.age == 31
    assert michael.id == None

def test_insert_row(database, Author):
    database.create(Author)

    michael = Author(name="Michael", age=31)
    database.save(michael)

    assert michael._get_insert_sql() ==  ('INSERT INTO author (age, name) VALUES (?, ?);', [31, 'Michael'])
    assert michael.id == 1

    john = Author(name="John", age=30)
    database.save(john)
    assert john.id == 2

    giulia = Author(name="Giulia", age=21)
    database.save(giulia)
    assert giulia.id == 3

    anna = Author(name="Anna", age=31)
    database.save(anna)
    assert anna.id == 4