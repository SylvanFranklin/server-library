"""Test suite for book_extractor module."""

from book_extractor import extract_book_titles, get_recommendations_for_text


def test_extract_single_book():
    """Test extracting a single book title."""
    text = "I really enjoyed reading Animal Farm by George Orwell."
    titles = extract_book_titles(text)
    print(f"Input: {text}")
    print(f"Extracted: {titles}")
    assert isinstance(titles, list)
    assert len(titles) > 0
    assert "Animal Farm" in titles
    print("✓ Single book extraction passed\n")


def test_extract_multiple_books():
    """Test extracting multiple book titles."""
    text = "I loved reading 1984, Animal Farm, and The Great Gatsby last summer."
    titles = extract_book_titles(text)
    print(f"Input: {text}")
    print(f"Extracted: {titles}")
    assert isinstance(titles, list)
    assert len(titles) >= 3
    print("✓ Multiple books extraction passed\n")


def test_extract_no_books():
    """Test when no book titles are mentioned."""
    text = "Today I went to the grocery store and bought some milk and bread."
    titles = extract_book_titles(text)
    print(f"Input: {text}")
    print(f"Extracted: {titles}")
    assert isinstance(titles, list)
    assert len(titles) == 0
    print("✓ No books extraction passed\n")


def test_extract_books_with_context():
    """Test extracting books from conversational text."""
    text = """
    Hey! I've been on a reading spree lately. First, I finished The Hobbit,
    then I moved on to Pride and Prejudice. After that, I couldn't put down
    The Catcher in the Rye. Have you read any of these?
    """
    titles = extract_book_titles(text)
    print(f"Input: {text.strip()}")
    print(f"Extracted: {titles}")
    assert isinstance(titles, list)
    assert len(titles) >= 3
    print("✓ Conversational context extraction passed\n")


def test_recommendations_pipeline():
    """Test the full recommendations pipeline."""
    text = "I absolutely love The Lord of the Rings and Harry Potter series."
    print(f"Input: {text}")
    results = get_recommendations_for_text(text)
    print(f"Found {len(results)} books:")
    for title, search_result in results.items():
        print(f"  - {title}: {search_result.num_found} results")
    assert isinstance(results, dict)
    assert len(results) > 0
    print("✓ Recommendations pipeline passed\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing book_extractor module")
    print("=" * 60 + "\n")

    try:
        test_extract_single_book()
        test_extract_multiple_books()
        test_extract_no_books()
        test_extract_books_with_context()
        test_recommendations_pipeline()

        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise
