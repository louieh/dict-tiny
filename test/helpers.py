from unittest.mock import MagicMock

from dict_tiny.translators.translator import DefaultTrans
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


def make_trans(text="hello", source_language=None, target_language=None):
    """Create a DefaultTrans instance with sensible defaults for testing."""
    mock_obj = MagicMock()
    mock_obj.source_language = source_language
    mock_obj.target_language = target_language
    mock_obj.wordbook = None
    mock_obj.more_detail = False
    trans = DefaultTrans(text, mock_obj)
    trans.name = "test"
    trans.display_name = "TestTrans"
    return trans
