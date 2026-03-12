"""Music artist extractor using local Ollama LLM + TheAudioDB pipeline.

Uses a local Ollama model to extract artist names from raw text,
then fetches search results for each artist from TheAudioDB.

BACKWARD COMPATIBLE: All original function signatures preserved.
"""

from audiodb import search_artist
from base_extractor import create_extractor
from local_llm_client import MUSIC_PROMPT_TEMPLATE


# Create the extractor functions using the factory pattern
extract_artist_names, get_recommendations_for_text = create_extractor(
    MUSIC_PROMPT_TEMPLATE,
    search_artist,
)


# Explicit exports for backward compatibility
__all__ = ["extract_artist_names", "get_recommendations_for_text"]
