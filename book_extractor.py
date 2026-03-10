"""Book title extractor using Ollama + Open Library pipeline.

Uses a local Ollama model to extract book titles from raw text,
then fetches search results for each title from Open Library.
"""

import json
import re
import ollama

from openlibrary import SearchResult, search_books


MODEL = "deepseek-r1:1.5b"

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)

_PROMPT_TEMPLATE = """\
Extract book titles from this text. Return a JSON array only.

Text: {text}

JSON array of book titles:"""


def extract_book_titles(text: str) -> list[str]:
    """Extract book titles from raw text using Ollama.

    Args:
        text: Raw text that may contain book title mentions.

    Returns:
        List of book title strings found in the text.

    Raises:
        json.JSONDecodeError: If the model output is not valid JSON.
    """
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": _PROMPT_TEMPLATE.format(text=text)}],
    )

    raw = response.message.content or ""

    # Strip <think>...</think> reasoning blocks emitted by deepseek-r1
    clean = _THINK_RE.sub("", raw).strip()

    # Strip markdown code blocks if present (```json ... ```)
    clean = re.sub(r"^```(?:json)?\n?", "", clean)
    clean = re.sub(r"\n?```$", "", clean)
    clean = clean.strip()

    # Handle empty response
    if not clean:
        return []

    # Parse JSON array
    titles = json.loads(clean)

    # Ensure it's a list and all items are strings
    if not isinstance(titles, list):
        raise ValueError(f"Expected JSON array, got {type(titles)}")

    return [str(title).strip() for title in titles if title]


def get_recommendations_for_text(text: str) -> dict[str, SearchResult]:
    """Extract book titles from text and fetch Open Library results for each.

    Args:
        text: Raw text that may contain book title mentions.

    Returns:
        Dict mapping each extracted book title to its Open Library SearchResult.
        Titles with no results are included with an empty SearchResult.

    Raises:
        json.JSONDecodeError: If the model output is not valid JSON.
    """
    titles = extract_book_titles(text)

    results: dict[str, SearchResult] = {}
    for title in titles:
        results[title] = search_books(title)

    return results
