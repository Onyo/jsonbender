import unittest

from jsonbender.core import K
from jsonbender.selectors import F, ProtectedF, S, OptionalS
from jsonbender.test import BenderTestMixin


class TestK(unittest.TestCase, BenderTestMixin):
    selector_cls = K

    def test_k(self):
        self.assert_bender(K(1), {}, 1)
        self.assert_bender(K('string'), {}, 'string')


class STestsMixin(BenderTestMixin):
    def test_no_selector_raises_value_error(self):
        self.assertRaises(ValueError, self.selector_cls)

    def test_shallow_existing_field(self):
        source = {'a': 'val'}
        self.assert_bender(self.selector_cls('a'), source, 'val')

    def test_deep_existing_path(self):
        source = {'a': [{}, {'b': 'ok!'}]}
        self.assert_bender(self.selector_cls('a', 1, 'b'), source, 'ok!')


class TestS(unittest.TestCase, STestsMixin):
    selector_cls = S

    def test_shallow_missing_field(self):
        self.assertRaises(KeyError, self.selector_cls('k'), {})

    def test_deep_missing_field(self):
        self.assertRaises(KeyError, self.selector_cls('k', 'k2'), {'k': {}})


class TestOptionalS(unittest.TestCase, STestsMixin):
    selector_cls = OptionalS

    def test_opts_without_default(self):
        bender = OptionalS('key', 'missing')
        self.assert_bender(bender, {'key': {}}, None)
        self.assert_bender(bender, {}, None)

    def test_opts_with_default(self):
        default = 27
        bender = OptionalS('key', 'missing', default=default)
        self.assert_bender(bender, {'key': {}}, default)
        self.assert_bender(bender, {}, default)

    def test_activate_on_IndexError(self):
        self.assert_bender(OptionalS(0), [], None)


class FTestsMixin(BenderTestMixin):
    def test_f(self):
        self.assert_bender(self.selector_cls(len), range(5), 5)

    def test_curry_kwargs(self):
        f = self.selector_cls(sorted, key=lambda d: d['v'])
        source = [{'v': 2}, {'v': 3}, {'v': 1}]
        self.assert_bender(f, source, [{'v': 1}, {'v': 2}, {'v': 3}])

    def test_protect(self):
        protected = self.selector_cls(int).protect(protect_against='bad')
        self.assertIsInstance(protected, ProtectedF)
        self.assert_bender(protected, '123', 123)
        self.assert_bender(protected, 'bad', 'bad')

    # TODO: move this to a more general Bender test
    def test_composition(self):
        s = S('val')
        f = self.selector_cls(len)
        source = {'val': 'hello'}
        self.assert_bender((f << s), source, 5)
        self.assert_bender((s >> f), source, 5)


class TestF(unittest.TestCase, FTestsMixin):
    selector_cls = F


class TestProtectedF(unittest.TestCase, FTestsMixin):
    selector_cls = ProtectedF

    def test_protectedf(self):
        protected = ProtectedF(int)
        self.assert_bender(protected, '123', 123)
        self.assert_bender(protected, None, None)


if __name__ == '__main__':
    unittest.main()

