"""Local LLM client using Ollama for entity extraction.

This module provides a unified interface for calling local Ollama models
to extract entities from text. Replaces the chatjimmy API with local inference.
"""

import json
import re
import subprocess


DEFAULT_MODEL = "deepseek-r1:1.5b"


def call_ollama(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Call Ollama with a prompt and return the response.

    Args:
        prompt: The prompt to send to the model.
        model: The Ollama model to use (default: deepseek-r1:1.5b).

    Returns:
        The model's response text.

    Raises:
        RuntimeError: If the Ollama call fails.
    """
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            check=True,
            timeout=60,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Ollama call failed: {e.stderr}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Ollama call timed out after 60 seconds")
    except FileNotFoundError:
        raise RuntimeError(
            "Ollama not found. Install from https://ollama.ai/ or ensure it's in PATH"
        )


def extract_entities(
    text: str,
    prompt_template: str,
    model: str = DEFAULT_MODEL,
) -> list[str]:
    """Extract entities from text using a local LLM.

    Args:
        text: Raw text to extract entities from.
        prompt_template: Template string with {text} placeholder for the extraction prompt.
        model: The Ollama model to use.

    Returns:
        List of extracted entity strings.

    Raises:
        json.JSONDecodeError: If the model output is not valid JSON.
        RuntimeError: If the Ollama call fails.
    """
    prompt = prompt_template.format(text=text)
    response = call_ollama(prompt, model=model)

    # Strip markdown code blocks if present (```json ... ```)
    clean = re.sub(r"^```(?:json)?\n?", "", response)
    clean = re.sub(r"\n?```$", "", clean)
    clean = clean.strip()

    # Handle empty response
    if not clean:
        return []

    # Parse JSON array
    entities = json.loads(clean)

    # Ensure it's a list and all items are strings
    if not isinstance(entities, list):
        raise ValueError(f"Expected JSON array, got {type(entities)}")

    return [str(entity).strip() for entity in entities if entity]


# Prompt templates for common extraction tasks
BOOK_PROMPT_TEMPLATE = """\
Extract all book titles mentioned in the following text.
Return ONLY a valid JSON array of book title strings, with no additional commentary or explanation.
If no book titles are mentioned, return an empty JSON array: []

Example format:
["The Great Gatsby", "1984", "To Kill a Mockingbird"]

Text: {text}"""


MUSIC_PROMPT_TEMPLATE = """\
Extract all music artist names mentioned in the following text.
Return ONLY a valid JSON array of artist name strings, with no additional commentary or explanation.
If no artist names are mentioned, return an empty JSON array: []

Example format:
["Coldplay", "Radiohead", "Daft Punk"]

Text: {text}"""


MOVIE_PROMPT_TEMPLATE = """\
Extract all movie titles mentioned in the following text.
Return ONLY a valid JSON array of movie title strings, with no additional commentary or explanation.
If no movie titles are mentioned, return an empty JSON array: []

Example format:
["The Godfather", "Inception", "Parasite"]

Text: {text}"""
