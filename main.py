import argparse
import httpx

from db import connect, init_db, get_user_books, get_user_artists, get_user_movies
from library import process_message


def cmd_add(conn, args):
    try:
        result = process_message(conn, args.username, args.text, args.media_type)
    except httpx.HTTPError as e:
        print(f"API error: {e}")
        return

    print(f"User: {result['user']}")
    if result["added"]:
        print(f"Added: {', '.join(result['added'])}")
    if result["skipped"]:
        print(f"No results for: {', '.join(result['skipped'])}")


def cmd_show(conn, args):
    if args.media_type in ("books", "all"):
        entries = get_user_books(conn, args.username)
        if entries:
            print(f"Books ({len(entries)}):")
            for e in entries:
                year = f" ({e.book.first_publish_year})" if e.book.first_publish_year else ""
                author = f" — {e.book.author_name[0]}" if e.book.author_name else ""
                print(f"  {e.book.title}{author}{year}  [{e.added_at}]")

    if args.media_type in ("music", "all"):
        entries = get_user_artists(conn, args.username)
        if entries:
            print(f"Music ({len(entries)}):")
            for e in entries:
                genre = f" ({e.artist.genre})" if e.artist.genre else ""
                print(f"  {e.artist.name}{genre}  [{e.added_at}]")

    if args.media_type in ("movies", "all"):
        entries = get_user_movies(conn, args.username)
        if entries:
            print(f"Movies ({len(entries)}):")
            for e in entries:
                year = f" ({e.movie.year})" if e.movie.year else ""
                print(f"  {e.movie.title}{year}  [{e.added_at}]")


def main():
    parser = argparse.ArgumentParser(description="server-library CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="extract media from text and save to db")
    add_p.add_argument("username")
    add_p.add_argument("media_type", choices=["books", "music", "movies"])
    add_p.add_argument("text")

    show_p = sub.add_parser("show", help="display a user's library")
    show_p.add_argument("username")
    show_p.add_argument("media_type", choices=["books", "music", "movies", "all"], default="all", nargs="?")

    args = parser.parse_args()
    conn = connect()
    init_db(conn)

    if args.command == "add":
        cmd_add(conn, args)
    elif args.command == "show":
        cmd_show(conn, args)


if __name__ == "__main__":
    main()
