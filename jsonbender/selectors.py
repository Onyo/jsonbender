from jsonbender.core import Bender


class K(Bender):
    """
    Selects a constant value.
    """
    def __init__(self, value):
        self._val = value

    def execute(self, source):
        return self._val


class S(Bender):
    """
    Selects a path of keys.
    Example:
        S('a', 0, 'b').execute({'a': [{'b': 42}]}) -> 42
    """
    def __init__(self, *path):
        if not path:
            raise ValueError('No path given')
        self._path = path

    def execute(self, source):
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
        OptionalS('a', 0, 'b', default=23).execute({'a': []}) -> 23
    """

    def __init__(self, *path, **kwargs):
        self.default = kwargs.get('default')
        super(OptionalS, self).__init__(*path)

    def execute(self, source):
        try:
            ret = super(OptionalS, self).execute(source)
        except LookupError:
            return self.default
        else:
            return ret


class ListS(S):
    """
    Greedily selects a path from a list of possible keys.
    Example:
        S(['a', 0], ['c']).execute({'a': [{'b': 42}]}, 'c': 0) -> {'b': 42}
        S(['b', 0], ['c']).execute({'a': [{'b': 42}]}, 'c': 0) -> 0
    """

    def execute(self, source):
        original_source = source
        for path in self._path:
            for key in path:
                try:
                    source = source[key]
                except (KeyError, IndexError, TypeError):
                    source = original_source
                    break
            else:
                return source

        # If self.default exists, this is an optional selector
        if hasattr(self, 'default'):
            return self.default

        raise TypeError(self._path)

    def optional(self, default=None):
        self.default = default
        return self


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

    def execute(self, value):
        return self._func(value, *self._args, **self._kwargs)

    def protect(self, protect_against=None):
        """
        Return a ProtectedF with the same parameters and with the given
        `protect_against`.
        """
        return ProtectedF(self._func,
                          *self._args,
                          protect_against=protect_against,
                          **self._kwargs)


class ProtectedF(F):
    """
    Similar to F.
    However, if the passing value equals the `protect_against` parameter,
    don't execute the function and return the passed value.

    `protect_against` defaults to None.
    Example:
    ```
        f = ProtectedF(lambda i: 1.0 / i, protect_against=0.0)
        f.execute(0)  # -> 0
    ```

    """
    def __init__(self, func, *args, **kwargs):
        self._protect_against = kwargs.pop('protect_against', None)
        super(ProtectedF, self).__init__(func, *args, **kwargs)

    def execute(self, value):
        if value == self._protect_against:
            return value
        else:
            return super(ProtectedF, self).execute(value)


