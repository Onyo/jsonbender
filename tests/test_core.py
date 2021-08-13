import sys
import unittest

from jsonbender import F, K, S
from jsonbender.core import BendingException, bend


class TestBend(unittest.TestCase):
    def test_empty_mapping(self):
        self.assertDictEqual(bend({}, {"a": 1}), {})

    def test_flat_mapping(self):
        mapping = {
            "a_field": S("a", "b"),
            "another_field": K("wow"),
        }
        source = {"a": {"b": "ok"}}
        expected = {
            "a_field": "ok",
            "another_field": "wow",
        }
        self.assertDictEqual(bend(mapping, source), expected)

    def test_nested_mapping(self):
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
        self.assertDictEqual(bend(mapping, source), expected)

    def test_nested_mapping_with_lists(self):
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
        self.assertDictEqual(bend(mapping, source), expected)

    def test_list_with_non_dict_elements(self):
        mapping = {"k": ["foo1", S("bar1")]}
        source = {"bar1": "val 1"}
        expected = {"k": ["foo1", "val 1"]}
        self.assertDictEqual(bend(mapping, source), expected)

    def test_bending_exception_is_raised_when_something_bad_happens(self):
        mapping = {"a": S("nonexistant")}
        source = {}
        self.assertRaises(BendingException, bend, mapping, source)

    def test_constants_without_K(self):
        mapping = {"a": "a const value", "b": 123}
        self.assertDictEqual(bend(mapping, {}), {"a": "a const value", "b": 123})


class TestOperators(unittest.TestCase):
    def test_add(self):
        assert (K(5) + K(2)).bend(None) == 7

    def test_sub(self):
        assert (K(5) - K(2)).bend(None) == 3

    def test_mul(self):
        assert (K(5) * K(2)).bend(None) == 10

    def test_div(self):
        assert (K(4) / K(2)).bend(None) == 2
        self.assertAlmostEqual((K(5) / K(2)).bend(None), 2.5, 2)

    def test_neg(self):
        assert (-K(1)).bend(None) == -1
        assert (-K(-1)).bend(None) == 1

    def test_eq(self):
        assert (K(42) == K(42)).bend(None)
        assert not (K(42) == K(27)).bend(None)

    def test_ne(self):
        assert not (K(42) != K(42)).bend(None)
        assert (K(42) != K(27)).bend(None)

    def test_and(self):
        assert (K(True) & K(True)).bend(None)
        assert not (K(True) & K(False)).bend(None)
        assert not (K(False) & K(True)).bend(None)
        assert not (K(False) & K(False)).bend(None)

    def test_or(self):
        assert (K(True) | K(True)).bend(None)
        assert (K(True) | K(False)).bend(None)
        assert (K(False) | K(True)).bend(None)
        assert not (K(False) | K(False)).bend(None)

    def test_invert(self):
        assert not (~K(True)).bend(None)
        assert (~K(False)).bend(None)


class TestGetItem(unittest.TestCase):
    def test_getitem(self):
        bender = S("val")[2:8:2]
        val = list(range(10))
        assert bender.bend({"val": val}) == [2, 4, 6]


class TestDict(unittest.TestCase):
    def test_function_with_dict(self):
        filter_none = F(lambda d: {k: v for k, v in d.items() if v is not None})
        b = filter_none << {"a": K(1), "b": K(None), "c": False}
        assert b.bend({}) == {"a": 1, "c": False}


class TestList(unittest.TestCase):
    def test_function_with_list(self):
        filter_none = F(lambda l: [v for v in l if v is not None])
        b = filter_none << [1, None, False]
        assert b.bend({}) == [1, False]
