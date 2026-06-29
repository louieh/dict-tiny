from dict_tiny.wordbook import WordBookEntry


def run_cli():
    """Run CLI and suppress SystemExit (plumbum exits via sys.exit by default)."""
    import pytest

    from dict_tiny.main import run

    try:
        run()
    except SystemExit:
        pass
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def _entry(**kw):
    """Create a WordBookEntry with defaults for testing."""
    defaults = dict(
        id=1,
        text="hello",
        source_language="en",
        target_language="ja",
        translator="youdaodict",
        timestamp=1000.0,
        last_access=1001.0,
        access_count=2,
    )
    defaults.update(kw)
    return WordBookEntry(**defaults)
