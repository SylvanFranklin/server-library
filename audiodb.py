"""TheAudioDB Music API wrapper.

This module provides a wrapper around the TheAudioDB API
for searching artists with minimal configuration.
"""

import httpx
from dataclasses import dataclass
from typing import Optional


@dataclass
class Artist:
    """Represents an artist from TheAudioDB API."""

    id: Optional[str]
    name: Optional[str]
    genre: Optional[str]
    biography: Optional[str]
    country: Optional[str]
    fanart_url: Optional[str]

    @classmethod
    def from_doc(cls, doc: dict) -> "Artist":
        """Create an Artist instance from API response document."""
        return cls(
            id=doc.get("idArtist"),
            name=doc.get("strArtist"),
            genre=doc.get("strGenre"),
            biography=doc.get("strBiographyEN"),
            country=doc.get("strCountry"),
            fanart_url=doc.get("strArtistFanart"),
        )


@dataclass
class ArtistSearchResult:
    """Represents the result of an artist search."""

    artists: list[Artist]


class AudioDBClient:
    """Client for TheAudioDB API."""

    BASE_URL = "https://www.theaudiodb.com/api/v1/json/123"

    def __init__(self, timeout: float = 30.0):
        """Initialize the AudioDB client.

        Args:
            timeout: Request timeout in seconds.
        """
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    def search_artist(self, name: str) -> ArtistSearchResult:
        """Search for an artist in TheAudioDB.

        Args:
            name: The artist name to search for.

        Returns:
            ArtistSearchResult containing matching artists (typically 0-1 due to free tier limit).

        Raises:
            httpx.HTTPError: If the API request fails.
        """
        params = {"s": name}
        url = f"{self.BASE_URL}/search.php"

        response = self.client.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        artists = [Artist.from_doc(doc) for doc in data.get("artists", [])]

        return ArtistSearchResult(artists=artists)

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def search_artist(name: str) -> ArtistSearchResult:
    """Convenience function to search for an artist.

    Args:
        name: The artist name to search for.

    Returns:
        ArtistSearchResult containing matching artists.
    """
    with AudioDBClient() as client:
        return client.search_artist(name)
