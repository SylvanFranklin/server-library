"""Movie title extractor using local Ollama LLM + OMDB pipeline.

Uses a local Ollama model to extract movie titles from raw text,
then fetches search results for each title from OMDB.

BACKWARD COMPATIBLE: All original function signatures preserved.
"""

from movies import MovieSearchResult, search_movies
from base_extractor import create_extractor
from local_llm_client import MOVIE_PROMPT_TEMPLATE


# Helper function to match original API signature (search_movies takes limit param)
def _search_movies_wrapper(title: str) -> MovieSearchResult:
    """Wrapper to match the expected signature for base_extractor."""
    return search_movies(title, limit=1)


# Create the extractor functions using the factory pattern
extract_movie_titles, get_recommendations_for_text = create_extractor(
    MOVIE_PROMPT_TEMPLATE,
    _search_movies_wrapper,
)


# Explicit exports for backward compatibility
__all__ = ["extract_movie_titles", "get_recommendations_for_text"]
