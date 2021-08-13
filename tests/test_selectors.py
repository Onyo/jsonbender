import unittest

from jsonbender.core import K
from jsonbender.selectors import F, OptionalS, ProtectedF, S


class TestK(unittest.TestCase):
    selector_cls = K

    def test_k(self):
        assert K(1).bend({}) == 1
        assert K("string").bend({}) == "string"


class STestsMixin:
    def test_no_selector_raises_value_error(self):
        self.assertRaises(ValueError, self.selector_cls)

    def test_shallow_existing_field(self):
        source = {"a": "val"}
        assert self.selector_cls("a").bend(source) == "val"

    def test_deep_existing_path(self):
        source = {"a": [{}, {"b": "ok!"}]}
        assert self.selector_cls("a", 1, "b").bend(source) == "ok!"


class TestS(unittest.TestCase, STestsMixin):
    selector_cls = S

    def test_shallow_missing_field(self):
        self.assertRaises(KeyError, self.selector_cls("k").bend, {})

    def test_deep_missing_field(self):
        self.assertRaises(KeyError, self.selector_cls("k", "k2").bend, {"k": {}})


class TestOptionalS(unittest.TestCase, STestsMixin):
    selector_cls = OptionalS

    def test_opts_without_default(self):
        bender = OptionalS("key", "missing")
        assert bender.bend({"key": {}}) is None
        assert bender.bend({}) is None

    def test_opts_with_default(self):
        default = 27
        bender = OptionalS("key", "missing", default=default)
        assert bender.bend({"key": {}}) == default
        assert bender.bend({}) == default

    def test_activate_on_IndexError(self):
        assert OptionalS(0).bend([]) is None


class FTestsMixin:
    def test_f(self):
        assert self.selector_cls(len).bend(range(5)) == 5

    def test_curry_kwargs(self):
        f = self.selector_cls(sorted, key=lambda d: d["v"])
        source = [{"v": 2}, {"v": 3}, {"v": 1}]
        assert f.bend(source) == [{"v": 1}, {"v": 2}, {"v": 3}]

    def test_protect(self):
        protected = self.selector_cls(int).protect(protect_against="bad")
        assert isinstance(protected, ProtectedF)
        assert protected.bend("123") == 123
        assert protected.bend("bad") == "bad"

    # TODO: move this to a more general Bender test
    def test_composition(self):
        s = S("val")
        f = self.selector_cls(len)
        source = {"val": "hello"}
        assert (f << s).bend(source) == 5
        assert (s >> f).bend(source) == 5


class TestF(unittest.TestCase, FTestsMixin):
    selector_cls = F


class TestProtectedF(unittest.TestCase, FTestsMixin):
    selector_cls = ProtectedF

    def test_protectedf(self):
        protected = ProtectedF(int)
        assert protected.bend("123") == 123
        assert protected.bend(None) is None
