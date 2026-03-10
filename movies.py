"""OMDB Movie API wrapper.

Requires an OMDB API key set via the OMDB_API_KEY environment variable.
Free keys available at https://www.omdbapi.com/apikey.aspx
"""

import os
import httpx
from dataclasses import dataclass
from typing import Optional


@dataclass
class Movie:
    """Represents a movie from the OMDB API."""

    imdb_id: Optional[str]
    title: Optional[str]
    year: Optional[str]
    poster_url: Optional[str]

    @classmethod
    def from_doc(cls, doc: dict) -> "Movie":
        return cls(
            imdb_id=doc.get("imdbID"),
            title=doc.get("Title"),
            year=doc.get("Year"),
            poster_url=doc.get("Poster"),
        )


@dataclass
class MovieSearchResult:
    movies: list[Movie]
    total_results: int


class OMDBClient:
    """Client for the OMDB API."""

    BASE_URL = "https://www.omdbapi.com"

    def __init__(self, api_key: Optional[str] = None, timeout: float = 30.0):
        self.api_key = api_key or os.environ.get("OMDB_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OMDB API key required. Set the OMDB_API_KEY environment variable "
                "or pass api_key= explicitly. Free keys at https://www.omdbapi.com/apikey.aspx"
            )
        self.client = httpx.Client(timeout=timeout)

    def search_movies(self, query: str, limit: int = 5) -> MovieSearchResult:
        """Search for movies by title.

        Args:
            query: Movie title to search for.
            limit: Maximum number of results to return (OMDB returns up to 10 per page).

        Returns:
            MovieSearchResult with matching movies and total count.

        Raises:
            httpx.HTTPError: If the API request fails.
            ValueError: If OMDB returns an error response.
        """
        response = self.client.get(
            self.BASE_URL,
            params={"s": query, "type": "movie", "apikey": self.api_key},
        )
        response.raise_for_status()
        data = response.json()

        if data.get("Response") == "False":
            return MovieSearchResult(movies=[], total_results=0)

        movies = [Movie.from_doc(doc) for doc in data.get("Search", [])][:limit]
        total = int(data.get("totalResults", 0))
        return MovieSearchResult(movies=movies, total_results=total)

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def search_movies(query: str, limit: int = 5) -> MovieSearchResult:
    """Convenience function to search for movies."""
    with OMDBClient() as client:
        return client.search_movies(query, limit=limit)
