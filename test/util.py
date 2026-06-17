from functools import wraps

import pytest

from dict_tiny.main import run


def assert_not_raises(test_func):
    @wraps(test_func)
    def wrapper(self):
        try:
            run()
        except SystemExit:
            pass
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

    return wrapper
