from jsonbender.core import Bender


class Format(Bender):
    """
    Return a formatted string just like `str.format()`.
    However, the values to be formatted are given by benders as positional or
    named parameters.

    `format_string` is a template with the same syntax as `str.format()`

    Example:
    ```
    fmt = Format('{} {} {last}', S('first'), S('second'), last=S('last'))
    source = {'first': 'Edsger', 'second': 'W.', 'last': 'Dijkstra'}
    fmt.bend(source)  # -> 'Edsger W. Dijkstra'
    ```
    """

    def __init__(self, format_string, *args, **kwargs):
        self._format_str = format_string
        self._positional_benders = args
        self._named_benders = kwargs

    def bend(self, source):
        args = [bender.bend(source) for bender in self._positional_benders]
        kwargs = {k: bender.bend(source) for k, bender in self._named_benders.items()}
        return self._format_str.format(*args, **kwargs)


class ProtectedFormat(Format):
    """
    Returns a formatted String, like Python's built-in format.
    If one of the arguments is None, it evaluates to None
    Examples:
        fmt = Format('{} {} {last}', S('first'), S('second'), last=S('last'))
        source = {'first': 'Edsger', 'second': 'W.', 'last': 'Dijkstra'}
        fmt.bend(source)  # -> 'Edsger W. Dijkstra'

        fmt = Format('{} {}', S('first'), S('second'))
        source = {'first': 'Edsger'}
        fmt.bend(source)  # -> None
    """

    def bend(self, source):
        # if any of the args to print are None, return None
        if any(
            [bender.bend(source) is None for bender in self._positional_benders]
            + [bender.bend(source) is None for bender in self._named_benders.values()]
        ):
            # create an object with property value=None so it can be processed
            return None
        # else just behave normally
        return super(ProtectedFormat, self).bend(source)
