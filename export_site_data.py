"""Export library.db contents to JSON for the Astro build."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

from db import connect, get_all_user_summaries, get_user_artists, get_user_books, get_user_movies


ROOT = Path(__file__).parent
OUTPUT_PATH = ROOT / "site-data" / "library.json"


def build_payload() -> dict:
    conn = connect()

    users = []
    for summary in get_all_user_summaries(conn):
        books = get_user_books(conn, summary.username)
        artists = get_user_artists(conn, summary.username)
        movies = get_user_movies(conn, summary.username)

        users.append(
            {
                "username": summary.username,
                "created_at": summary.created_at,
                "counts": {
                    "books": summary.book_count,
                    "music": summary.artist_count,
                    "movies": summary.movie_count,
                },
                "books": [
                    {
                        "title": entry.book.title,
                        "author": entry.book.author_name[0] if entry.book.author_name else None,
                        "year": entry.book.first_publish_year,
                        "added_at": entry.added_at,
                    }
                    for entry in books
                ],
                "music": [
                    {
                        "name": entry.artist.name,
                        "genre": entry.artist.genre,
                        "country": entry.artist.country,
                        "added_at": entry.added_at,
                    }
                    for entry in artists
                ],
                "movies": [
                    {
                        "title": entry.movie.title,
                        "year": entry.movie.year,
                        "added_at": entry.added_at,
                    }
                    for entry in movies
                ],
            }
        )

    total_books = sum(user["counts"]["books"] for user in users)
    total_music = sum(user["counts"]["music"] for user in users)
    total_movies = sum(user["counts"]["movies"] for user in users)

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "totals": {
            "users": len(users),
            "books": total_books,
            "music": total_music,
            "movies": total_movies,
        },
        "users": users,
    }


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(build_payload(), indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
