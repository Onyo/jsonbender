from jsonbender.core import Bender, K


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

    def __init__(self, condition, when_true=K(None), when_false=K(None)):
        self.condition = condition
        self.when_true = when_true
        self.when_false = when_false

    def bend(self, val):
        return self.when_true.bend(val) if self.condition.bend(val) else self.when_false.bend(val)


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
        self.benders = benders

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

    def __init__(self, key_bender, cases, default=None):
        self.key_bender = key_bender
        self.cases = cases
        self.default = default

    def bend(self, source):
        key = self.key_bender.bend(source)
        try:
            bender = self.cases[key]
        except LookupError:
            if self.default:
                bender = self.default
            else:
                raise

        return bender.bend(source)
