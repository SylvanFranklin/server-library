"""Book title extractor using local Ollama LLM + Open Library pipeline.

Uses a local Ollama model to extract book titles from raw text,
then fetches search results for each title from Open Library.

BACKWARD COMPATIBLE: All original function signatures preserved.
"""

from openlibrary import search_books
from base_extractor import create_extractor
from local_llm_client import BOOK_PROMPT_TEMPLATE


# Create the extractor functions using the factory pattern
extract_book_titles, get_recommendations_for_text = create_extractor(
    BOOK_PROMPT_TEMPLATE,
    search_books,
)


# Explicit exports for backward compatibility
__all__ = ["extract_book_titles", "get_recommendations_for_text"]
