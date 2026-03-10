"""Music artist extractor using chatjimmy API + TheAudioDB pipeline.

Uses the free chatjimmy.ai API to extract artist names from raw text,
then fetches search results for each artist from TheAudioDB.
"""

import gzip
import json
import re
import sys
import urllib.error
import urllib.request

from audiodb import ArtistSearchResult, search_artist


API_URL = "https://chatjimmy.ai/api/chat"
MODEL = "llama3.1-8B"

HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/json",
    "Origin": "https://chatjimmy.ai",
    "Referer": "https://chatjimmy.ai/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}

STATS_RE = re.compile(r"<\|stats\|>.*?<\|/stats\|>", re.DOTALL)

_PROMPT_TEMPLATE = """\
Extract all music artist names mentioned in the following text.
Return ONLY a valid JSON array of artist name strings, with no additional commentary or explanation.
If no artist names are mentioned, return an empty JSON array: []

Example format:
["Coldplay", "Radiohead", "Daft Punk"]

Text: {text}"""


def _call_api(message: str) -> str | None:
    """Call the chatjimmy API and return the parsed response.

    Args:
        message: The message to send to the API.

    Returns:
        Parsed response text, or None if the request fails.
    """
    payload = json.dumps(
        {
            "messages": [{"role": "user", "content": message}],
            "chatOptions": {
                "selectedModel": MODEL,
                "systemPrompt": "",
                "topK": 8,
            },
            "attachment": None,
        }
    ).encode()

    req = urllib.request.Request(API_URL, data=payload, headers=HEADERS, method="POST")

    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            if resp.getheader("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return _parse_response(raw.decode())
    except urllib.error.HTTPError as e:
        body = e.read()
        if e.headers.get("Content-Encoding") == "gzip":
            body = gzip.decompress(body)
        print(f"[http {e.code}] {body.decode()}", file=sys.stderr)
    except urllib.error.URLError as e:
        print(f"[network error] {e.reason}", file=sys.stderr)

    return None


def _parse_response(raw: str) -> str:
    """Extract clean text from a streamed API response.

    Args:
        raw: The raw response string from the API.

    Returns:
        Cleaned response text.
    """
    parts = []
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("0:"):
            try:
                parts.append(json.loads(line[2:]))
            except json.JSONDecodeError:
                pass

    text = "".join(parts) if parts else raw
    return STATS_RE.sub("", text).strip()


def extract_artist_names(text: str) -> list[str]:
    """Extract artist names from raw text using chatjimmy API.

    Args:
        text: Raw text that may contain artist name mentions.

    Returns:
        List of artist name strings found in the text.

    Raises:
        json.JSONDecodeError: If the model output is not valid JSON.
        RuntimeError: If the API call fails.
    """
    response = _call_api(_PROMPT_TEMPLATE.format(text=text))

    if response is None:
        raise RuntimeError("Failed to call chatjimmy API")

    clean = response.strip()

    # Strip markdown code blocks if present (```json ... ```)
    clean = re.sub(r"^```(?:json)?\n?", "", clean)
    clean = re.sub(r"\n?```$", "", clean)
    clean = clean.strip()

    # Handle empty response
    if not clean:
        return []

    # Parse JSON array
    names = json.loads(clean)

    # Ensure it's a list and all items are strings
    if not isinstance(names, list):
        raise ValueError(f"Expected JSON array, got {type(names)}")

    return [str(name).strip() for name in names if name]


def get_recommendations_for_text(text: str) -> dict[str, ArtistSearchResult]:
    """Extract artist names from text and fetch TheAudioDB results for each.

    Args:
        text: Raw text that may contain artist name mentions.

    Returns:
        Dict mapping each extracted artist name to its TheAudioDB ArtistSearchResult.
        Artists with no results are included with an empty ArtistSearchResult.

    Raises:
        json.JSONDecodeError: If the model output is not valid JSON.
        RuntimeError: If the API call fails.
    """
    names = extract_artist_names(text)

    results: dict[str, ArtistSearchResult] = {}
    for name in names:
        results[name] = search_artist(name)

    return results
