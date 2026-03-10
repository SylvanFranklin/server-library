"""Test suite for music_extractor module."""

from music_extractor import extract_artist_names, get_recommendations_for_text


def test_extract_single_artist():
    """Test extracting a single artist name."""
    text = "I really love Coldplay's music."
    names = extract_artist_names(text)
    print(f"Input: {text}")
    print(f"Extracted: {names}")
    assert isinstance(names, list)
    assert len(names) > 0
    assert "Coldplay" in names
    print("✓ Single artist extraction passed\n")


def test_extract_multiple_artists():
    """Test extracting multiple artist names."""
    text = "I like Radiohead, Daft Punk, and Björk. They're all amazing."
    names = extract_artist_names(text)
    print(f"Input: {text}")
    print(f"Extracted: {names}")
    assert isinstance(names, list)
    assert len(names) >= 3
    print("✓ Multiple artists extraction passed\n")


def test_extract_no_artists():
    """Test when no artist names are mentioned."""
    text = "Today I went to the grocery store and bought some milk and bread."
    names = extract_artist_names(text)
    print(f"Input: {text}")
    print(f"Extracted: {names}")
    assert isinstance(names, list)
    assert len(names) == 0
    print("✓ No artists extraction passed\n")


def test_extract_artists_with_context():
    """Test extracting artists from conversational text."""
    text = """
    Hey! I've been listening to so much music lately. First, I got into The Beatles,
    then I discovered Jimi Hendrix. After that, I couldn't stop listening to
    Pink Floyd. Have you heard any of these artists?
    """
    names = extract_artist_names(text)
    print(f"Input: {text.strip()}")
    print(f"Extracted: {names}")
    assert isinstance(names, list)
    assert len(names) >= 3
    print("✓ Conversational context extraction passed\n")


def test_recommendations_pipeline():
    """Test the full recommendations pipeline."""
    text = "I absolutely love The Rolling Stones and David Bowie."
    print(f"Input: {text}")
    results = get_recommendations_for_text(text)
    print(f"Found {len(results)} artists:")
    for name, search_result in results.items():
        artist_count = len(search_result.artists)
        if artist_count > 0:
            artist = search_result.artists[0]
            print(f"  - {name}: Found artist (ID: {artist.id})")
        else:
            print(f"  - {name}: No results")
    assert isinstance(results, dict)
    assert len(results) > 0
    print("✓ Recommendations pipeline passed\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing music_extractor module")
    print("=" * 60 + "\n")

    try:
        test_extract_single_artist()
        test_extract_multiple_artists()
        test_extract_no_artists()
        test_extract_artists_with_context()
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
