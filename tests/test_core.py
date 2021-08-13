import pytest

from jsonbender import F, K, S
from jsonbender.core import BendingException, bend


class TestBend:
    @staticmethod
    def test_empty_mapping():
        assert bend({}, {"a": 1}) == {}

    @staticmethod
    def test_flat_mapping():
        mapping = {
            "a_field": S("a", "b"),
            "another_field": K("wow"),
        }
        source = {"a": {"b": "ok"}}
        expected = {
            "a_field": "ok",
            "another_field": "wow",
        }
        assert bend(mapping, source) == expected

    @staticmethod
    def test_nested_mapping():
        mapping = {
            "a_field": S("a", "b"),
            "a": {
                "nested": {
                    "field": S("f1", "f2"),
                },
            },
        }
        source = {
            "a": {"b": "ok"},
            "f1": {"f2": "hi"},
        }
        expected = {
            "a_field": "ok",
            "a": {"nested": {"field": "hi"}},
        }
        assert bend(mapping, source) == expected

    @staticmethod
    def test_nested_mapping_with_lists():
        mapping = {
            "a_field": S("a", "b"),
            "a": [
                {
                    "nested": {
                        "field": S("f1", "f2"),
                    },
                }
            ],
        }
        source = {
            "a": {"b": "ok"},
            "f1": {"f2": "hi"},
        }
        expected = {
            "a_field": "ok",
            "a": [{"nested": {"field": "hi"}}],
        }
        assert bend(mapping, source) == expected

    @staticmethod
    def test_list_with_non_dict_elements():
        mapping = {"k": ["foo1", S("bar1")]}
        source = {"bar1": "val 1"}
        expected = {"k": ["foo1", "val 1"]}
        assert bend(mapping, source) == expected

    @staticmethod
    def test_bending_exception_is_raised_when_something_bad_happens():
        mapping = {"a": S("nonexistant")}
        source = {}
        with pytest.raises(BendingException):
            bend(mapping, source)

    @staticmethod
    def test_constants_without_K():
        mapping = {"a": "a const value", "b": 123}
        assert bend(mapping, {}) == {"a": "a const value", "b": 123}


class TestOperators:
    @staticmethod
    def test_add():
        assert (K(5) + K(2)).bend(None) == 7

    @staticmethod
    def test_sub():
        assert (K(5) - K(2)).bend(None) == 3

    @staticmethod
    def test_mul():
        assert (K(5) * K(2)).bend(None) == 10

    @staticmethod
    def test_div():
        assert (K(4) / K(2)).bend(None) == 2
        assert (K(5) / K(2)).bend(None) == pytest.approx(2.5, 0.1)

    @staticmethod
    def test_neg():
        assert (-K(1)).bend(None) == -1
        assert (-K(-1)).bend(None) == 1

    @staticmethod
    def test_eq():
        assert (K(42) == K(42)).bend(None)
        assert not (K(42) == K(27)).bend(None)

    @staticmethod
    def test_ne():
        assert not (K(42) != K(42)).bend(None)
        assert (K(42) != K(27)).bend(None)

    @staticmethod
    def test_and():
        assert (K(True) & K(True)).bend(None)
        assert not (K(True) & K(False)).bend(None)
        assert not (K(False) & K(True)).bend(None)
        assert not (K(False) & K(False)).bend(None)

    @staticmethod
    def test_or():
        assert (K(True) | K(True)).bend(None)
        assert (K(True) | K(False)).bend(None)
        assert (K(False) | K(True)).bend(None)
        assert not (K(False) | K(False)).bend(None)

    @staticmethod
    def test_invert():
        assert not (~K(True)).bend(None)
        assert (~K(False)).bend(None)


class TestGetItem:
    @staticmethod
    def test_getitem():
        bender = S("val")[2:8:2]
        val = list(range(10))
        assert bender.bend({"val": val}) == [2, 4, 6]


class TestDict:
    @staticmethod
    def test_function_with_dict():
        filter_none = F(lambda d: {k: v for k, v in d.items() if v is not None})
        b = filter_none << {"a": K(1), "b": K(None), "c": False}
        assert b.bend({}) == {"a": 1, "c": False}


class TestList:
    @staticmethod
    def test_function_with_list():
        filter_none = F(lambda l: [v for v in l if v is not None])
        b = filter_none << [1, None, False]
        assert b.bend({}) == [1, False]
