"""Base extractor functionality for media entity extraction.

This module provides shared utilities for all extractor modules
to reduce code duplication across book, music, and movie extractors.
"""

from typing import TypeVar, Callable
from local_llm_client import extract_entities


# Type variables for generic extractor
EntityType = TypeVar("EntityType")
ResultType = TypeVar("ResultType")


def create_extractor(
    prompt_template: str,
    api_search_func: Callable[[str], ResultType],
    model: str = "deepseek-r1:1.5b",
) -> tuple[Callable[[str], list[str]], Callable[[str], dict[str, ResultType]]]:
    """Factory function to create entity extractor and recommendation functions.

    This eliminates duplication across book/music/movie extractors by providing
    a common pattern for: extract entities → fanout to API → return results dict.

    Args:
        prompt_template: Template string with {text} placeholder for entity extraction.
        api_search_func: Function that takes an entity name and returns search results.
        model: The Ollama model to use for extraction.

    Returns:
        Tuple of (extract_func, recommendations_func):
        - extract_func(text) -> list[str]: Extracts entity names from text
        - recommendations_func(text) -> dict[str, ResultType]: Extracts and fetches results

    Example:
        >>> from openlibrary import search_books
        >>> from local_llm_client import BOOK_PROMPT_TEMPLATE
        >>> extract_books, get_book_recs = create_extractor(
        ...     BOOK_PROMPT_TEMPLATE,
        ...     search_books
        ... )
        >>> books = extract_books("I love reading 1984 and Dune")
        >>> results = get_book_recs("I love reading 1984 and Dune")
    """

    def extract_func(text: str) -> list[str]:
        """Extract entity names from raw text using local LLM.

        Args:
            text: Raw text that may contain entity mentions.

        Returns:
            List of entity name strings found in the text.

        Raises:
            json.JSONDecodeError: If the model output is not valid JSON.
            RuntimeError: If the LLM call fails.
        """
        return extract_entities(text, prompt_template, model=model)

    def recommendations_func(text: str) -> dict[str, ResultType]:
        """Extract entities from text and fetch API results for each.

        Args:
            text: Raw text that may contain entity mentions.

        Returns:
            Dict mapping each extracted entity name to its API search result.
            Entities with no results are included with empty/default results.

        Raises:
            json.JSONDecodeError: If the model output is not valid JSON.
            RuntimeError: If the LLM call fails.
        """
        entities = extract_func(text)

        results: dict[str, ResultType] = {}
        for entity in entities:
            results[entity] = api_search_func(entity)

        return results

    return extract_func, recommendations_func
