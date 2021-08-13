class BenderTestMixin:
    @staticmethod
    def assert_bender(bender, source, expected_value, msg=None):
        got = bender.bend(source)
        assert got == expected_value
