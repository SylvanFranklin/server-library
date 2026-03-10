"""Test script for Open Library API wrapper."""

from openlibrary import search_books, OpenLibraryClient


def test_basic_search():
    """Test basic book search functionality."""
    print("Testing basic book search...")
    results = search_books("the lord of the rings", limit=5)

    print(f"\nFound {results.num_found} books total")
    print(f"Showing {len(results.docs)} results (offset {results.start}):\n")

    for i, book in enumerate(results.docs, 1):
        print(f"{i}. {book.title}")
        if book.author_name:
            print(f"   Authors: {', '.join(book.author_name)}")
        if book.first_publish_year:
            print(f"   First Published: {book.first_publish_year}")
        print(f"   Editions: {book.edition_count}")
        print()


def test_sorted_search():
    """Test search with sorting."""
    print("Testing search sorted by newest...")
    results = search_books("python programming", limit=3, sort="new")

    print(f"\nFound {results.num_found} books (sorted by newest)\n")

    for i, book in enumerate(results.docs, 1):
        print(f"{i}. {book.title}")
        if book.first_publish_year:
            print(f"   Year: {book.first_publish_year}")
        print()


def test_context_manager():
    """Test using the client as a context manager."""
    print("Testing context manager usage...")

    with OpenLibraryClient() as client:
        results = client.search_books("harry potter", limit=3)

    print(f"Found {results.num_found} books\n")

    for book in results.docs:
        print(f"- {book.title}")
        if book.cover_i:
            print(f"  Cover ID: {book.cover_i}")


if __name__ == "__main__":
    test_basic_search()
    print("\n" + "=" * 50 + "\n")
    test_sorted_search()
    print("\n" + "=" * 50 + "\n")
    test_context_manager()
