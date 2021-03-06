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


def test_get_all(database, Author):
    database.create(Author)

    michael = Author(name="Michael", age=31)
    giulia = Author(name="Giulia", age=21)
    database.save(michael)
    database.save(giulia)

    rows = database.all(Author)
    
    assert Author._get_select_all_sql() == ("SELECT id, age, name FROM author;", ["id", "age", "name"])
    assert {row.name for row in rows}  == {"Michael", "Giulia"}
    assert {row.age for row in rows} == { 31, 21 }


def test_get_one(database, Author):
    database.create(Author)
    michael = Author(name="Michael", age=31)
    database.save(michael)

    michael_from_db = database.get(Author, id=1)
    michael._get_select_sql(id=1) == ("SELECT id, age, name FROM author WHERE (id=?);", ["id", "age", "name"], [1])

    assert type(michael_from_db) == Author
    assert michael_from_db.id == michael.id
    assert michael_from_db.name == michael.name
    assert michael_from_db.age == michael.age


def test_get_book(database, Author, Book):
    database.create(Author)
    database.create(Book)
    john = Author(name="John Doe", age=43)
    arash = Author(name="Arash Kun", age=50)
    book = Book(title="Building an ORM", published=False, author=john)
    book2 = Book(title="Scoring Goals", published=True, author=arash)
    database.save(john)
    database.save(arash)
    database.save(book)
    database.save(book2)

    book_from_db = database.get(Book, 2)

    assert book_from_db.title == "Scoring Goals"
    assert book_from_db.author.name == "Arash Kun"
    assert book_from_db.author.id == 2


def test_update_author(database, Author):
    database.create(Author)
    john = Author(name="John Doe", age=23)
    database.save(john)

    john.age = 43
    john.name = "John Wick"
    database.update(john)

    john_from_db = database.get(Author, id=john.id)

    assert john_from_db.age == 43
    assert john_from_db.name == "John Wick"

def test_delete_author(database, Author):
    database.create(Author)
    john = Author(name="John Doe", age=23)
    database.save(john)
    id = john.id

    database.delete(john)
    assert john._get_delete_sql() == ("DELETE FROM author where id = ?;", [id])
    all_authors = database.all(Author)

    assert len(all_authors) == 0
