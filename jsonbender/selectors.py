from jsonbender.core import Bender, Protected


class S(Bender):
    """
    Selects a path of keys.
    Example:
        S('a', 0, 'b').bend({'a': [{'b': 42}]}) -> 42
    """

    def __init__(self, *path):
        if not path:
            raise ValueError("No path given")
        self._path = path

    def bend(self, source):
        for key in self._path:
            source = source[key]
        return source

    def optional(self, default=None):
        """
        Return an OptionalS with the same path and with the given `default`.
        """
        return OptionalS(*self._path, default=default)


class OptionalS(S):
    """
    Similar to S. However, if any of the keys doesn't exist, returns the
    `default` value.

    `default` defaults to None.
    Example:
        OptionalS('a', 0, 'b', default=23).bend({'a': []}) -> 23
    """

    def __init__(self, *path, **kwargs):
        self.default = kwargs.get("default")
        super().__init__(*path)

    def bend(self, source):
        try:
            ret = super().bend(source)
        except LookupError:
            return self.default
        else:
            return ret


class F(Bender):
    """
    Lifts a python callable into a Bender, so it can be composed.
    The extra positional and named parameters are passed to the function at
    bending time after the given value.

    `func` is a callable

    Example:
    ```
    f = F(sorted, key=lambda d: d['id'])
    K([{'id': 3}, {'id': 1}]) >> f  #  -> [{'id': 1}, {'id': 3}]
    ```
    """

    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def bend(self, source):
        return self._func(source, *self._args, **self._kwargs)


def ProtectedF(func, *args, **kwargs):
    """Backwards compatibility for ProtectedF()."""
    protect_against = kwargs.pop("protect_against", None)
    return Protected(F(func, *args, **kwargs), protect_against)
