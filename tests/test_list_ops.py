import unittest
from operator import add

from jsonbender import K, S, bend
from jsonbender.list_ops import Filter, FlatForall, Forall, ForallBend, ListOp, Reduce


class ListOpTestCase(unittest.TestCase):
    cls = ListOp

    def assert_list_op(self, the_list, func, expected_value):
        assert self.cls(func).bend(the_list) == expected_value


class TestForall(ListOpTestCase):
    cls = Forall

    def test_empty_list(self):
        self.assert_list_op([], lambda i: i * 2, [])

    def test_nonempty_list(self):
        self.assert_list_op(range(1, 5), lambda i: i * 2, [2, 4, 6, 8])

    def test_compatibility(self):
        # TODO: remove this when compatibility is broken
        bender = self.cls(K([1]), lambda i: i)
        assert bender.bend({}) == [1]


class TestForallBend(ListOpTestCase):
    cls = ForallBend

    def test_bend(self):
        self.assert_list_op([{"a": 23}, {"a": 27}], {"b": S("a")}, [{"b": 23}, {"b": 27}])


class TestReduce(ListOpTestCase):
    cls = Reduce

    def test_empty_list(self):
        bender = Reduce(add)
        self.assertRaises(ValueError, bender.bend, [])

    def test_nonempty_list(self):
        self.assert_list_op(range(1, 5), add, 10)

    def test_compatibility(self):
        # TODO: remove this when compatibility is broken
        assert self.cls(K([1, 2]), add).bend({}) == 3


class TestFilter(ListOpTestCase):
    cls = Filter

    def test_empty_list(self):
        self.assert_list_op([], lambda d: not d["ignore"], [])

    def test_nonempty_list(self):
        the_list = [
            {"id": 1, "ignore": True},
            {"id": 2, "ignore": False},
            {"id": 3, "ignore": False},
            {"id": 4, "ignore": True},
        ]

        expected = [{"id": 2, "ignore": False}, {"id": 3, "ignore": False}]
        self.assert_list_op(the_list, lambda d: not d["ignore"], expected)

    def test_compatibility(self):
        # TODO: remove this on next release
        assert self.cls(K([1]), lambda i: True).bend({}) == [1]


class TestFlatForall(ListOpTestCase):
    cls = FlatForall

    def test_empty_list(self):
        self.assert_list_op([], lambda d: d["b"], [])

    def test_nonempty_list(self):
        self.assert_list_op([{"b": [1, 2]}, {"b": [-2, -1]}], lambda d: d["b"], [1, 2, -2, -1])

    def test_compatibility(self):
        # TODO: remove this on next release
        assert self.cls(K([1]), lambda i: [i]).bend({}) == [1]
