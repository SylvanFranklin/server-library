"""SQLite database layer for server-library."""

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from openlibrary import Book
from audiodb import Artist
from movies import Movie


@dataclass
class UserBook:
    book: Book
    added_at: str


@dataclass
class UserArtist:
    artist: Artist
    added_at: str


@dataclass
class UserMovie:
    movie: Movie
    added_at: str

DB_PATH = Path(__file__).parent / "library.db"


def connect(path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id                INTEGER PRIMARY KEY,
            discord_username  TEXT    NOT NULL UNIQUE,
            created_at        TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS books (
            id                 INTEGER PRIMARY KEY,
            ol_key             TEXT    UNIQUE,
            title              TEXT,
            author             TEXT,
            first_publish_year INTEGER,
            cover_i            INTEGER
        );

        CREATE TABLE IF NOT EXISTS artists (
            id         INTEGER PRIMARY KEY,
            audiodb_id TEXT    UNIQUE,
            name       TEXT,
            genre      TEXT,
            country    TEXT
        );

        CREATE TABLE IF NOT EXISTS user_books (
            user_id    INTEGER NOT NULL REFERENCES users(id),
            book_id    INTEGER NOT NULL REFERENCES books(id),
            added_at   TEXT    NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (user_id, book_id, added_at)
        );

        CREATE TABLE IF NOT EXISTS user_artists (
            user_id    INTEGER NOT NULL REFERENCES users(id),
            artist_id  INTEGER NOT NULL REFERENCES artists(id),
            added_at   TEXT    NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (user_id, artist_id, added_at)
        );

        CREATE TABLE IF NOT EXISTS movies (
            id         INTEGER PRIMARY KEY,
            imdb_id    TEXT    UNIQUE,
            title      TEXT,
            year       TEXT,
            poster_url TEXT
        );

        CREATE TABLE IF NOT EXISTS user_movies (
            user_id    INTEGER NOT NULL REFERENCES users(id),
            movie_id   INTEGER NOT NULL REFERENCES movies(id),
            added_at   TEXT    NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (user_id, movie_id, added_at)
        );
    """)
    conn.commit()


def upsert_user(conn: sqlite3.Connection, discord_username: str) -> int:
    conn.execute(
        "INSERT OR IGNORE INTO users (discord_username) VALUES (?)",
        (discord_username,),
    )
    conn.commit()
    row = conn.execute(
        "SELECT id FROM users WHERE discord_username = ?", (discord_username,)
    ).fetchone()
    return row["id"]


def upsert_book(conn: sqlite3.Connection, book: Book) -> int:
    author = book.author_name[0] if book.author_name else None
    conn.execute(
        """
        INSERT INTO books (ol_key, title, author, first_publish_year, cover_i)
        VALUES (:key, :title, :author, :year, :cover)
        ON CONFLICT (ol_key) DO UPDATE SET
            title              = excluded.title,
            author             = excluded.author,
            first_publish_year = excluded.first_publish_year,
            cover_i            = excluded.cover_i
        """,
        {"key": book.key, "title": book.title, "author": author,
         "year": book.first_publish_year, "cover": book.cover_i},
    )
    conn.commit()
    row = conn.execute(
        "SELECT id FROM books WHERE ol_key = ?", (book.key,)
    ).fetchone()
    return row["id"]


def upsert_artist(conn: sqlite3.Connection, artist: Artist) -> int:
    conn.execute(
        """
        INSERT INTO artists (audiodb_id, name, genre, country)
        VALUES (:audiodb_id, :name, :genre, :country)
        ON CONFLICT (audiodb_id) DO UPDATE SET
            name    = excluded.name,
            genre   = excluded.genre,
            country = excluded.country
        """,
        {"audiodb_id": artist.id, "name": artist.name,
         "genre": artist.genre, "country": artist.country},
    )
    conn.commit()
    row = conn.execute(
        "SELECT id FROM artists WHERE audiodb_id = ?", (artist.id,)
    ).fetchone()
    return row["id"]


def add_user_book(conn: sqlite3.Connection, user_id: int, book_id: int) -> None:
    conn.execute(
        "INSERT INTO user_books (user_id, book_id) VALUES (?, ?)",
        (user_id, book_id),
    )
    conn.commit()


def add_user_artist(conn: sqlite3.Connection, user_id: int, artist_id: int) -> None:
    conn.execute(
        "INSERT INTO user_artists (user_id, artist_id) VALUES (?, ?)",
        (user_id, artist_id),
    )
    conn.commit()


def upsert_movie(conn: sqlite3.Connection, movie: Movie) -> int:
    conn.execute(
        """
        INSERT INTO movies (imdb_id, title, year, poster_url)
        VALUES (:imdb_id, :title, :year, :poster_url)
        ON CONFLICT (imdb_id) DO UPDATE SET
            title      = excluded.title,
            year       = excluded.year,
            poster_url = excluded.poster_url
        """,
        {"imdb_id": movie.imdb_id, "title": movie.title,
         "year": movie.year, "poster_url": movie.poster_url},
    )
    conn.commit()
    row = conn.execute(
        "SELECT id FROM movies WHERE imdb_id = ?", (movie.imdb_id,)
    ).fetchone()
    return row["id"]


def add_user_movie(conn: sqlite3.Connection, user_id: int, movie_id: int) -> None:
    conn.execute(
        "INSERT INTO user_movies (user_id, movie_id) VALUES (?, ?)",
        (user_id, movie_id),
    )
    conn.commit()


def get_user_books(conn: sqlite3.Connection, username: str) -> list[UserBook]:
    rows = conn.execute(
        """
        SELECT b.ol_key, b.title, b.author, b.first_publish_year, b.cover_i,
               ub.added_at
        FROM books b
        JOIN user_books ub ON b.id = ub.book_id
        JOIN users u ON ub.user_id = u.id
        WHERE u.discord_username = ?
        ORDER BY ub.added_at DESC
        """,
        (username,),
    ).fetchall()

    return [
        UserBook(
            book=Book(
                key=row["ol_key"],
                title=row["title"],
                author_name=[row["author"]] if row["author"] else [],
                first_publish_year=row["first_publish_year"],
                edition_count=0,
                cover_i=row["cover_i"],
                ia=None,
            ),
            added_at=row["added_at"],
        )
        for row in rows
    ]


def get_user_artists(conn: sqlite3.Connection, username: str) -> list[UserArtist]:
    rows = conn.execute(
        """
        SELECT a.audiodb_id, a.name, a.genre, a.country,
               ua.added_at
        FROM artists a
        JOIN user_artists ua ON a.id = ua.artist_id
        JOIN users u ON ua.user_id = u.id
        WHERE u.discord_username = ?
        ORDER BY ua.added_at DESC
        """,
        (username,),
    ).fetchall()

    return [
        UserArtist(
            artist=Artist(
                id=row["audiodb_id"],
                name=row["name"],
                genre=row["genre"],
                biography=None,
                country=row["country"],
                fanart_url=None,
            ),
            added_at=row["added_at"],
        )
        for row in rows
    ]


def get_user_movies(conn: sqlite3.Connection, username: str) -> list[UserMovie]:
    rows = conn.execute(
        """
        SELECT m.imdb_id, m.title, m.year, m.poster_url,
               um.added_at
        FROM movies m
        JOIN user_movies um ON m.id = um.movie_id
        JOIN users u ON um.user_id = u.id
        WHERE u.discord_username = ?
        ORDER BY um.added_at DESC
        """,
        (username,),
    ).fetchall()

    return [
        UserMovie(
            movie=Movie(
                imdb_id=row["imdb_id"],
                title=row["title"],
                year=row["year"],
                poster_url=row["poster_url"],
            ),
            added_at=row["added_at"],
        )
        for row in rows
    ]
