import unittest
from operator import add

from jsonbender import K, S, bend
from jsonbender.control_flow import Alternation, If, Switch
from jsonbender.test import BenderTestMixin


class TestIf(BenderTestMixin, unittest.TestCase):
    def setUp(self):
        self.na_li = {"country": "China", "first_name": "Li", "last_name": "Na"}
        self.guga = {"country": "Brazil", "first_name": "Gustavo", "last_name": "Kuerten"}

    def test_if_true(self):
        if_ = If(S("country") == K("China"), S("first_name"), S("last_name"))
        self.assert_bender(if_, self.na_li, "Li")

    def test_if_false(self):
        if_ = If(S("country") == K("China"), S("first_name"), S("last_name"))
        self.assert_bender(if_, self.guga, "Kuerten")

    def test_if_true_default(self):
        if_ = If(S("country") == K("China"), when_false=S("last_name"))
        self.assert_bender(if_, self.na_li, None)

    def test_if_false_default(self):
        if_ = If(S("country") == K("China"), S("first_name"))
        self.assert_bender(if_, self.guga, None)


class TestAlternation(BenderTestMixin, unittest.TestCase):
    def test_empty_benders(self):
        self.assertRaises(ValueError, Alternation().bend, {})

    def test_matches(self):
        bender = Alternation(S(1), S(0), S("key1"))
        self.assert_bender(bender, ["a", "b"], "b")
        self.assert_bender(bender, ["a"], "a")
        self.assert_bender(bender, {"key1": 23}, 23)

    def test_no_match(self):
        self.assertRaises(IndexError, Alternation(S(1)).bend, [])
        self.assertRaises(KeyError, Alternation(S(1)).bend, {})


class TestSwitch(BenderTestMixin, unittest.TestCase):
    def test_match(self):
        bender = Switch(
            S("service"),
            {"twitter": S("handle"), "mastodon": S("handle") + K("@") + S("server")},
            default=S("email"),
        )

        self.assert_bender(bender, {"service": "twitter", "handle": "etandel"}, "etandel")
        self.assert_bender(
            bender,
            {"service": "mastodon", "handle": "etandel", "server": "mastodon.social"},
            "etandel@mastodon.social",
        )

    def test__no_match_with_default(self):
        bender = Switch(
            S("service"),
            {"twitter": S("handle"), "mastodon": S("handle") + K("@") + S("server")},
            default=S("email"),
        )
        self.assert_bender(
            bender, {"service": "facebook", "email": "email@whatever.com"}, "email@whatever.com"
        )

    def test__no_match_without_default(self):
        self.assertRaises(KeyError, Switch(S("key"), {}).bend, {"key": None})


if __name__ == "__main__":
    unittest.main()
