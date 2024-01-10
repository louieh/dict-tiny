import unittest
from unittest.mock import patch

from test.util import assert_not_raises

"""
    @classmethod
    def run(
        cls,
        argv=None,
        exit=True,  # pylint: disable=redefined-builtin
    ):
        '''
        Runs the application, taking the arguments from ``sys.argv`` by default if
        nothing is passed. If ``exit`` is
        ``True`` (the default), the function will exit with the appropriate return code;
        otherwise it will return a tuple of ``(inst, retcode)``, where ``inst`` is the
        application instance created internally by this function and ``retcode`` is the
        exit code of the application.

        .. note::
           Setting ``exit`` to ``False`` is intendend for testing/debugging purposes only -- do
           not override it in other situations.
        '''
        if argv is None:
            argv = sys.argv
        cls.autocomplete(argv)
        argv = list(argv)
        inst = cls(argv.pop(0))
"""


class TestCLI(unittest.TestCase):
    @patch("sys.argv", [""])
    @assert_not_raises
    def test_cli_init(self):
        pass

    @patch("sys.argv", ["", "-c"])
    @assert_not_raises
    def test_clipBoard(self):
        pass


if __name__ == '__main__':
    unittest.main()
