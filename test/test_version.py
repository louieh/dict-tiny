"""Tests for dict_tiny.version module.

Verifies that package metadata is accessible and values are reasonable.
"""


class TestVersion:
    """Package metadata correctness."""

    def test_version_is_string(self):
        from dict_tiny.version import __version__

        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_name_is_string(self):
        from dict_tiny.version import name

        assert isinstance(name, str)
        assert len(name) > 0

    def test_description_is_string(self):
        from dict_tiny.version import DESCRIPTION

        assert isinstance(DESCRIPTION, str)
        assert len(DESCRIPTION) > 0

    def test_version_format(self):
        """Version string should follow semver-like pattern."""
        from dict_tiny.version import __version__

        parts = __version__.split(".")
        assert len(parts) >= 3

    def test_name_matches_package(self):
        from dict_tiny.version import name

        assert name == "dict-tiny"
