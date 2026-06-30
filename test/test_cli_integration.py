from unittest.mock import patch

import pytest

from test.helpers import run_cli


@pytest.mark.integration
class TestCliIntegration:
    """Smoke tests that call real APIs (no mocking).
    Marked with @pytest.mark.integration so they can be skipped in CI.
    """

    @patch("sys.argv", ["", "-y", "book"])
    def test_cli_youdao_translate(self):
        run_cli()

    @patch("sys.argv", ["", "-y", "book", "--target-language", "ja"])
    def test_cli_youdao_japanese(self):
        run_cli()

    @patch("sys.argv", ["", "-g", "book"])
    def test_cli_google_translate(self):
        """Google Translate translates 'book' via real API."""
        run_cli()

    @patch("sys.argv", ["", "-g", "book", "--source-language", "en", "--target-language", "zh"])
    def test_cli_google_translate_en_to_zh(self):
        """Google Translate translates English to Chinese via real API."""
        run_cli()
