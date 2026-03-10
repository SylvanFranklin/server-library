"""Movie title extractor using chatjimmy API + OMDB pipeline."""

import gzip
import json
import re
import sys
import urllib.error
import urllib.request

from movies import MovieSearchResult, search_movies


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
Extract all movie titles mentioned in the following text.
Return ONLY a valid JSON array of movie title strings, with no additional commentary or explanation.
If no movie titles are mentioned, return an empty JSON array: []

Example format:
["The Godfather", "Inception", "Parasite"]

Text: {text}"""


def _call_api(message: str) -> str | None:
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


def extract_movie_titles(text: str) -> list[str]:
    """Extract movie titles from raw text using chatjimmy API."""
    response = _call_api(_PROMPT_TEMPLATE.format(text=text))

    if response is None:
        raise RuntimeError("Failed to call chatjimmy API")

    clean = response.strip()
    clean = re.sub(r"^```(?:json)?\n?", "", clean)
    clean = re.sub(r"\n?```$", "", clean)
    clean = clean.strip()

    if not clean:
        return []

    titles = json.loads(clean)

    if not isinstance(titles, list):
        raise ValueError(f"Expected JSON array, got {type(titles)}")

    return [str(title).strip() for title in titles if title]


def get_recommendations_for_text(text: str) -> dict[str, MovieSearchResult]:
    """Extract movie titles from text and fetch OMDB results for each."""
    titles = extract_movie_titles(text)

    results: dict[str, MovieSearchResult] = {}
    for title in titles:
        results[title] = search_movies(title, limit=1)

    return results
