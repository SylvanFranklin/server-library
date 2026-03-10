"""Top-level pipeline: username + text + media_type → database."""

from typing import Literal
from sqlite3 import Connection

from book_extractor import extract_book_titles
from music_extractor import extract_artist_names
from movie_extractor import extract_movie_titles
from openlibrary import search_books
from audiodb import search_artist
from movies import search_movies
from db import (
    upsert_user, upsert_book, upsert_artist, upsert_movie,
    add_user_book, add_user_artist, add_user_movie,
)


def process_message(
    conn: Connection,
    username: str,
    text: str,
    media_type: Literal["books", "music", "movies"],
) -> dict:
    """Extract media from text and persist to the database.

    Args:
        conn:       Open database connection.
        username:   Discord username of the user who sent the message.
        text:       Raw message text to extract media from.
        media_type: "books" or "music" — determines which extractor runs.

    Returns:
        Summary dict with keys "user", "added", and "skipped".
        "added" is a list of titles/names that were saved.
        "skipped" is a list that had no API results.
    """
    user_id = upsert_user(conn, username)
    added = []
    skipped = []

    if media_type == "books":
        titles = extract_book_titles(text)
        for title in titles:
            result = search_books(title, limit=1)
            if not result.docs:
                skipped.append(title)
                continue
            book = result.docs[0]
            book_id = upsert_book(conn, book)
            add_user_book(conn, user_id, book_id)
            added.append(book.title or title)

    elif media_type == "music":
        names = extract_artist_names(text)
        for name in names:
            result = search_artist(name)
            if not result.artists:
                skipped.append(name)
                continue
            artist = result.artists[0]
            artist_id = upsert_artist(conn, artist)
            add_user_artist(conn, user_id, artist_id)
            added.append(artist.name or name)

    elif media_type == "movies":
        titles = extract_movie_titles(text)
        for title in titles:
            result = search_movies(title, limit=1)
            if not result.movies:
                skipped.append(title)
                continue
            movie = result.movies[0]
            movie_id = upsert_movie(conn, movie)
            add_user_movie(conn, user_id, movie_id)
            added.append(movie.title or title)

    return {"user": username, "added": added, "skipped": skipped}
