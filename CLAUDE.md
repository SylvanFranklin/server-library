# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run tests (tests are plain Python scripts, not pytest)
python test_openlibrary.py
python test_book_extractor.py
python test_music_extractor.py

# Run the chatjimmy CLI
python jimmy.py
python jimmy.py -m "your message"

# Lint
ruff check .
ruff format .
```

## Architecture

This project is a media metadata library that pipelines free LLM entity extraction into external API lookups.

**API wrappers** (`openlibrary.py`, `audiodb.py`): Thin `httpx`-based clients with dataclasses for responses. Both expose a context-manager class (`OpenLibraryClient`, `AudioDBClient`) and a module-level convenience function. All fields are `Optional` to handle incomplete API responses.

**Extractor modules** (`book_extractor.py`, `music_extractor.py`): Use the free chatjimmy.ai API (no key required) to extract entity names from raw text via a JSON-array prompt, then fan out to the respective API wrapper for each entity. The main pipeline function is `get_recommendations_for_text(text) -> dict[name, SearchResult]`.

**chatjimmy response parsing**: The API returns an SSE-style stream where content lines start with `0:` and contain JSON-encoded string fragments. Stats metadata is wrapped in `<|stats|>...<|/stats|>` tags and stripped. Both extractors and `jimmy.py` duplicate this parsing logic.

**Planned additions** (see README): database layer, SSG for website output, GitHub Actions deploy, nmemos bot connector, additional media APIs (movies, etc.).
