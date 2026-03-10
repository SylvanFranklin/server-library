# server-library

A media library backend that extracts book, music, and movie references from natural language text, looks them up against public APIs, and persists them to a per-user SQLite database.

## What it does

When given a Discord username, a media type, and a raw message, the pipeline:

1. Sends the text to the free [chatjimmy.ai](https://chatjimmy.ai) LLM and asks it to extract entity names as a JSON array
2. Looks each name up against the appropriate public API
3. Upserts the result into SQLite and records the user → media association with a timestamp

**Supported media types:**

| Type | Extraction | API |
|------|-----------|-----|
| `books` | Book titles | [Open Library](https://openlibrary.org/developers/api) — no key required |
| `music` | Artist names | [TheAudioDB](https://www.theaudiodb.com/api_guide.php) — no key required |
| `movies` | Movie titles | [OMDB](https://www.omdbapi.com) — free key required |

## Usage

```bash
# Install dependencies
uv sync

# Add media from a message
python main.py add <username> books  "I've been rereading 1984 and Animal Farm"
python main.py add <username> music  "been listening to a lot of Radiohead and Portishead"
python main.py add <username> movies "just watched Parasite and Everything Everywhere All at Once"

# Show a user's library
python main.py show <username>          # all categories
python main.py show <username> books
python main.py show <username> music
python main.py show <username> movies
```

OMDB requires an API key (free at https://www.omdbapi.com/apikey.aspx):

```bash
export OMDB_API_KEY=your_key_here
```

## Connecting to nmemos

nmemos needs to call into this library in two places:

**1. `/library <type>` command handler**

When a user runs `/library books`, `/library music`, or `/library movies`, nmemos should grab the content of the previous message and call:

```python
from db import connect, init_db
from library import process_message

conn = connect()
init_db(conn)

result = process_message(conn, discord_username, previous_message_text, media_type)
# result = {"user": "...", "added": [...], "skipped": [...]}
```

Reply to the user with `result["added"]` (saved) and `result["skipped"]` (no API results found).

**2. Displaying a user's library**

When a user wants to see their saved media:

```python
from db import connect, get_user_books, get_user_artists, get_user_movies

conn = connect()
books   = get_user_books(conn, discord_username)    # list[UserBook]
artists = get_user_artists(conn, discord_username)  # list[UserArtist]
movies  = get_user_movies(conn, discord_username)   # list[UserMovie]
```

Each entry has a `.added_at` timestamp and the full API metadata object (`.book`, `.artist`, `.movie`).

The `connect()` call will use `library.db` in the project root by default. Pass a `Path` to `connect()` if nmemos needs the database at a different location.

## Roadmap

- [x] Book extraction + Open Library API
- [x] Music extraction + TheAudioDB API
- [x] Movie extraction + OMDB API
- [x] SQLite database with per-user history
- [ ] SSG to generate a static website from the database
- [ ] GitHub Action to auto-deploy the website
- [ ] nmemos `/library` command integration
