from functools import wraps

from dict_tiny.main import run


def assert_not_raises(test_func):
    @wraps(test_func)
    def wrapper(self):
        try:
            run()
        except SystemExit:
            pass
        except Exception as e:
            self.fail(f"Unexpected exception: {e}")

    return wrapper
