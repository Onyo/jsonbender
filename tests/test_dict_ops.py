import unittest

from jsonbender import S, bend, Context, K
from jsonbender.dict_ops import ForallDict
from jsonbender.list_ops import ListOp
from jsonbender.selectors import Second, First
from jsonbender.test import BenderTestMixin


class DictOpTestCase(unittest.TestCase, BenderTestMixin):
    cls = ListOp

    def assert_list_op(self, the_list, func, expected_value):
        self.assert_bender(self.cls(func), the_list, expected_value)


class TestForall(DictOpTestCase):
    cls = ForallDict

    def test_empty_dict(self):
        self.assert_list_op({}, lambda i: i, [])

    def test_example(self):
        self.assert_list_op({'a': 'b', 'c': 'd'}, lambda v: v[0] + v[1], ['ab', 'cd'])

    def test_compatibility(self):
        # TODO: remove this when compatibility is broken
        bender = self.cls(K({'a': 'b'}), lambda i: i)
        self.assert_bender(bender, {}, [('a', 'b')])

    def test_bend_example(self):
        source = {'a': {'b': 1}, 'c': {'b': 2}}
        self.assert_bender(self.cls.bend({'b2': Second() >> S('b'), 'identifier': First()}),
                           source,
                           [{'b2': 1, 'identifier': 'a'}, {'b2': 2, 'identifier': 'c'}])

    def test_bend_with_context(self):
        mapping = {'b': Context() >> S('c')}
        context = {'c': 42}
        self.assert_bender(self.cls.bend(mapping, context),
                           {'a': {}, 'd': {}},
                           [{'b': 42}, {'b': 42}])

    def test_bend_inherits_outer_context_by_default(self):
        inner_mapping = {'val': Context()}
        outer_mapping = {'a': S('items') >> self.cls.bend(inner_mapping)}
        source = {'items': {'a': 'a', 'b': 'b', 'c': 'c'}}
        got = bend(outer_mapping, source, context=27)
        expected = {'a': [{'val': 27}, {'val': 27}, {'val': 27}]}
        self.assertEqual(got, expected)