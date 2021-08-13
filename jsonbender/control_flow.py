from jsonbender.core import Bender, K, benderify


class If(Bender):
    """
    Takes a condition bender, and two benders (both default to K(None)).
    If the condition bender evaluates to true, return the value of the first
    bender. If it evaluates to false, return the value of the second bender.

    Example:
    ```
    if_ = If(S('country') == K('China'), S('first_name'), S('last_name'))
    if_({'country': 'China',
         'first_name': 'Li',
         'last_name': 'Na'})  # ->  'Li'

    if_({'country': 'Brazil',
         'first_name': 'Gustavo',
         'last_name': 'Kuerten'})  # -> 'Kuerten'
    ```
    """

    def __init__(self, condition, when_true=None, when_false=None):
        self.condition = benderify(condition)
        self.when_true = benderify(when_true)
        self.when_false = benderify(when_false)

    def bend(self, source):
        return (
            self.when_true.bend(source)
            if self.condition.bend(source)
            else self.when_false.bend(source)
        )


class Alternation(Bender):
    """
    Take any number of benders, and return the value of the first one that
    doesn't raise a LookupError (KeyError, IndexError etc.).
    If all benders raise LookupError, re-raise the last raised exception.

    Example:
    ```
    b = Alternation(S(1), S(0), S('key1'))
    b(['a', 'b'])  #  -> 'b'
    b(['a'])  #  -> 'a'
    b([])  #  -> KeyError
    b({})  #  -> KeyError
    b({'key1': 23})  # -> 23
    ```
    """

    def __init__(self, *benders):
        self.benders = [benderify(b) for b in benders]

    def bend(self, source):
        exc = ValueError()
        for bender in self.benders:
            try:
                result = bender.bend(source)
            except LookupError as e:
                exc = e
            else:
                return result
        else:
            raise exc


class Switch(Bender):
    """
    Take a key bender, a 'case' container of benders and a default bender
    (optional).
    The value returned by the key bender is used to get a bender from the
    case container, which then returns the result.
    If the key is not in the case container, the default is used.
    If it's unavailable, raise the original LookupError.

    Example:
    ```
    b = Switch(S('service'),
               {'twitter': S('handle'),
                'mastodon': S('handle') + K('@') + S('server')},
               default=S('email'))

    b({'service': 'twitter', 'handle': 'etandel'})  #  -> 'etandel'
    b({'service': 'mastodon', 'handle': 'etandel',
       'server': 'mastodon.social'})  #  -> 'etandel@mastodon.social'
    b({'service': 'facebook',
       'email': 'email@whatever.com'})  #  -> 'email@whatever.com'
    ```
    """

    class NoValue:
        pass

    def __init__(self, key_bender, cases, default=NoValue):
        self.key_bender = benderify(key_bender)
        self.cases = {k: benderify(v) for k, v in cases.items()}
        self.default = benderify(default) if default is not self.NoValue else None

    def bend(self, source):
        key = self.key_bender.bend(source)
        try:
            bender = self.cases[key]
        except KeyError:
            if self.default is None:
                raise
            bender = self.default

        return bender.bend(source)
