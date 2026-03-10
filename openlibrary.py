"""Open Library Search API wrapper.

This module provides a wrapper around the Open Library Search API
for searching books with minimal configuration.
"""

import httpx
from dataclasses import dataclass
from typing import Optional


@dataclass
class Book:
    """Represents a book from Open Library Search API."""

    key: Optional[str]
    title: Optional[str]
    author_name: list[str]
    first_publish_year: Optional[int]
    edition_count: int
    cover_i: Optional[int]
    ia: Optional[list[str]]

    @classmethod
    def from_doc(cls, doc: dict) -> "Book":
        """Create a Book instance from API response document."""
        return cls(
            key=doc.get("key"),
            title=doc.get("title"),
            author_name=doc.get("author_name", []),
            first_publish_year=doc.get("first_publish_year"),
            edition_count=doc.get("edition_count", 0),
            cover_i=doc.get("cover_i"),
            ia=doc.get("ia"),
        )


@dataclass
class SearchResult:
    """Represents the result of a book search."""

    num_found: int
    start: int
    docs: list[Book]


class OpenLibraryClient:
    """Client for Open Library Search API."""

    BASE_URL = "https://openlibrary.org"

    def __init__(self, timeout: float = 30.0):
        """Initialize the Open Library client.

        Args:
            timeout: Request timeout in seconds.
        """
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    def search_books(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        sort: Optional[str] = None,
    ) -> SearchResult:
        """Search for books in Open Library.

        Args:
            query: The search query string.
            limit: Maximum number of results to return (default: 10).
            offset: Number of results to skip for pagination (default: 0).
            sort: Sort order. Options: 'new', 'old', 'random', 'key',
                  or other facets. Default is relevance.

        Returns:
            SearchResult containing matching books and pagination info.

        Raises:
            httpx.HTTPError: If the API request fails.
        """
        params = {
            "q": query,
            "limit": limit,
            "offset": offset,
        }

        if sort:
            params["sort"] = sort

        url = f"{self.BASE_URL}/search.json"

        response = self.client.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        books = [Book.from_doc(doc) for doc in data.get("docs", [])]

        return SearchResult(
            num_found=data.get("num_found", 0),
            start=data.get("start", 0),
            docs=books,
        )

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def search_books(
    query: str,
    limit: int = 10,
    offset: int = 0,
    sort: Optional[str] = None,
) -> SearchResult:
    """Convenience function to search for books.

    Args:
        query: The search query string.
        limit: Maximum number of results to return (default: 10).
        offset: Number of results to skip for pagination (default: 0).
        sort: Sort order. Options: 'new', 'old', 'random', 'key'.

    Returns:
        SearchResult containing matching books and pagination info.
    """
    with OpenLibraryClient() as client:
        return client.search_books(query, limit=limit, offset=offset, sort=sort)
