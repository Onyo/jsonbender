from jsonbender import K, S
from jsonbender.string_ops import Format, ProtectedFormat


class TestFormat:
    @staticmethod
    def test_format():
        bender = Format("{} {} {} {noun}.", K("This"), K("is"), K("a"), noun=K("test"))
        assert bender.bend(None) == "This is a test."


class TestProtectedFormat:
    @staticmethod
    def test_format():
        bender = ProtectedFormat(
            "{} {} {} {noun}.",
            K("This"),
            K("is"),
            K("a"),
            noun=S("noun").optional(),
        )
        assert bender.bend({}) is None
        assert bender.bend({"noun": "test"}) == "This is a test."
