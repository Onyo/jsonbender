import unittest

from jsonbender import K, S
from jsonbender.string_ops import Format, ProtectedFormat
from jsonbender.test import BenderTestMixin


class TestFormat(unittest.TestCase, BenderTestMixin):
    def test_format(self):
        bender = Format("{} {} {} {noun}.", K("This"), K("is"), K("a"), noun=K("test"))
        self.assert_bender(bender, None, "This is a test.")


class TestProtectedFormat(unittest.TestCase):
    def test_format(self):
        bender = ProtectedFormat(
            "{} {} {} {noun}.",
            K("This"),
            K("is"),
            K("a"),
            noun=S("noun").optional(),
        )
        assert bender.bend({}) is None
        assert bender.bend({"noun": "test"}) == "This is a test."
