class BenderTestMixin(object):
    def assert_bender(self, bender, source, expected_value, msg=None):
        got = bender.bend(source)
        assert got == expected_value
