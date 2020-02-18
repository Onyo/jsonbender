import unittest

import sys

from jsonbender import S, K, F
from jsonbender.core import bend, BendingException
from jsonbender.test import BenderTestMixin


class TestBend(unittest.TestCase):
    def test_empty_mapping(self):
        self.assertDictEqual(bend({}, {'a': 1}), {})

    def test_flat_mapping(self):
        mapping = {
            'a_field': S('a', 'b'),
            'another_field': K('wow'),
        }
        source = {'a': {'b': 'ok'}}
        expected = {
            'a_field': 'ok',
            'another_field': 'wow',
        }
        self.assertDictEqual(bend(mapping, source), expected)

    def test_nested_mapping(self):
        mapping = {
            'a_field': S('a', 'b'),
            'a': {
                'nested': {
                    'field': S('f1', 'f2'),
                },
            },
        }
        source = {
            'a': {'b': 'ok'},
            'f1': {'f2': 'hi'},
        }
        expected = {
            'a_field': 'ok',
            'a': {'nested': {'field': 'hi'}},
        }
        self.assertDictEqual(bend(mapping, source), expected)

    def test_nested_mapping_with_lists(self):
        mapping = {
            'a_field': S('a', 'b'),
            'a': [{
                'nested': {
                    'field': S('f1', 'f2'),
                },
            }],
        }
        source = {
            'a': {'b': 'ok'},
            'f1': {'f2': 'hi'},
        }
        expected = {
            'a_field': 'ok',
            'a': [{'nested': {'field': 'hi'}}],
        }
        self.assertDictEqual(bend(mapping, source), expected)

    def test_list_with_non_dict_elements(self):
        mapping = {'k': ['foo1', S('bar1')]}
        source = {'bar1': 'val 1'}
        expected = {'k': ['foo1', 'val 1']}
        self.assertDictEqual(bend(mapping, source), expected)

    def test_bending_exception_is_raised_when_something_bad_happens(self):
        mapping = {'a': S('nonexistant')}
        source = {}
        self.assertRaises(BendingException, bend, mapping, source)

    def test_constants_without_K(self):
        mapping = {'a': 'a const value', 'b': 123}
        self.assertDictEqual(bend(mapping, {}),
                             {'a': 'a const value', 'b': 123})


class TestOperators(unittest.TestCase, BenderTestMixin):
    def test_add(self):
        self.assert_bender(K(5) + K(2), None, 7)

    def test_sub(self):
        self.assert_bender(K(5) - K(2), None, 3)

    def test_mul(self):
        self.assert_bender(K(5) * K(2), None, 10)

    def test_div(self):
        self.assert_bender(K(4) / K(2), None, 2)
        self.assertAlmostEqual((K(5) / K(2)).bend(None), 2.5, 2)

    def test_neg(self):
        self.assert_bender(-K(1), None, -1)
        self.assert_bender(-K(-1), None, 1)

    def test_eq(self):
        self.assert_bender(K(42) == K(42), None, True)
        self.assert_bender(K(42) == K(27), None, False)

    def test_ne(self):
        self.assert_bender(K(42) != K(42), None, False)
        self.assert_bender(K(42) != K(27), None, True)

    def test_and(self):
        self.assert_bender(K(True) & K(True), None, True)
        self.assert_bender(K(True) & K(False), None, False)
        self.assert_bender(K(False) & K(True), None, False)
        self.assert_bender(K(False) & K(False), None, False)

    def test_or(self):
        self.assert_bender(K(True) | K(True), None, True)
        self.assert_bender(K(True) | K(False), None, True)
        self.assert_bender(K(False) | K(True), None, True)
        self.assert_bender(K(False) | K(False), None, False)

    def test_invert(self):
        self.assert_bender(~K(True), None, False)
        self.assert_bender(~K(False), None, True)


class TestGetItem(unittest.TestCase, BenderTestMixin):
    def test_getitem(self):
        bender = S('val')[2:8:2]
        if sys.version_info.major == 2:
            val = range(10)
        else:
            val = list(range(10))
        self.assert_bender(bender, {'val': val}, [2, 4, 6])


class TestDict(unittest.TestCase, BenderTestMixin):
    def test_function_with_dict(self):
        filter_none = F(lambda d: {k: v for k, v in d.items() if v is not None})
        b = filter_none << {'a': K(1), 'b': K(None), 'c': False}
        self.assert_bender(b, {}, {'a': 1, 'c': False})


class TestList(unittest.TestCase, BenderTestMixin):
    def test_function_with_list(self):
        filter_none = F(lambda l: [v for v in l if v is not None])
        b = filter_none << [1, None, False]
        self.assert_bender(b, {}, [1, False])


if __name__ == '__main__':
    unittest.main()
