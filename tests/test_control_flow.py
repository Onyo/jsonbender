import unittest
from operator import add

from jsonbender import K, S, bend
from jsonbender.control_flow import Alternation, If, Switch


class TestIf(unittest.TestCase):
    def setUp(self):
        self.na_li = {"country": "China", "first_name": "Li", "last_name": "Na"}
        self.guga = {"country": "Brazil", "first_name": "Gustavo", "last_name": "Kuerten"}

    def test_if_true(self):
        if_ = If(S("country") == K("China"), S("first_name"), S("last_name"))
        assert if_.bend(self.na_li) == "Li"

    def test_if_false(self):
        if_ = If(S("country") == K("China"), S("first_name"), S("last_name"))
        assert if_.bend(self.guga) == "Kuerten"

    def test_if_true_default(self):
        if_ = If(S("country") == K("China"), when_false=S("last_name"))
        assert if_.bend(self.na_li) is None

    def test_if_false_default(self):
        if_ = If(S("country") == K("China"), S("first_name"))
        assert if_.bend(self.guga) is None


class TestAlternation(unittest.TestCase):
    def test_empty_benders(self):
        self.assertRaises(ValueError, Alternation().bend, {})

    def test_matches(self):
        bender = Alternation(S(1), S(0), S("key1"))
        assert bender.bend(["a", "b"]) == "b"
        assert bender.bend(["a"]) == "a"
        assert bender.bend({"key1": 23}) == 23

    def test_no_match(self):
        self.assertRaises(IndexError, Alternation(S(1)).bend, [])
        self.assertRaises(KeyError, Alternation(S(1)).bend, {})


class TestSwitch(unittest.TestCase):
    def test_match(self):
        bender = Switch(
            S("service"),
            {"twitter": S("handle"), "mastodon": S("handle") + K("@") + S("server")},
            default=S("email"),
        )

        assert bender.bend({"service": "twitter", "handle": "etandel"}) == "etandel"
        assert (
            bender.bend({"service": "mastodon", "handle": "etandel", "server": "mastodon.social"})
            == "etandel@mastodon.social"
        )

    def test__no_match_with_default(self):
        bender = Switch(
            S("service"),
            {"twitter": S("handle"), "mastodon": S("handle") + K("@") + S("server")},
            default=S("email"),
        )
        assert (
            bender.bend({"service": "facebook", "email": "email@whatever.com"})
            == "email@whatever.com"
        )

    def test__no_match_without_default(self):
        self.assertRaises(KeyError, Switch(S("key"), {}).bend, {"key": None})
