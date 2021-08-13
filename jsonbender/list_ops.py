from functools import reduce
from itertools import chain
from warnings import warn

from jsonbender.core import Bender, bend


class ListOp(Bender):
    """
    Base class for operations on lists.
    Subclasses must implement the op() method, which takes the function passed
    to the operator's __init__(), an iterable, and should return the
    desired result.
    """

    def __init__(self, *args):
        if len(args) == 1:
            self._func = args[0]
            self._bender = None
        # TODO: this is here for compatibility reasons.
        elif len(args) == 2:
            self._bender, self._func = args
            msg = (
                "Passing a bender to {0} is deprecated."
                "Please use {0} in a composition chain "
                "(see docs for more details).".format(type(self).__name__)
            )
            warn(DeprecationWarning(msg))
        else:
            msg = "{} constructor only takes one parameter, {} given".format(
                type(self).__name__, len(args)
            )
            raise TypeError(msg)

    def op(self, func, vals):
        raise NotImplementedError()

    def bend(self, source):
        # TODO: this is here for compatibility reasons
        if self._bender:
            source = self._bender.bend(source)
        return self.op(self._func, source)


class Forall(ListOp):
    """
    Similar to Python's map().
    Builds a new list by applying the given function to each element of the
    iterable.

    Example:
    ```
    Forall(lambda i: i * 2).bend(range(5))  # -> [0, 2, 4, 6, 8]
    ```
    """

    def op(self, func, vals):
        return list(map(func, vals))


class ForallBend(Forall):
    """
    Bends each element of the list with given mapping and context.

    mapping: a JSONBender mapping as passed to the `bend()` function.
    """

    def __init__(self, mapping, context=None):
        self._mapping = mapping
        # TODO this is here for retrocompatibility reasons.
        # remove this when ListOp also breaks retrocompatibility
        self._bender = None

    def bend(self, source):
        self._func = lambda v: bend(self._mapping, v)
        return super().bend(source)


class Reduce(ListOp):
    """
    Similar to Python's reduce().
    Reduces an iterable into a single value by repeatedly applying the given
    function to the elements.
    The function must accept two parameters: the first is the accumulator (the
    value returned from the last call), which defaults to the first element of
    the iterable (it must be nonempty); the second is the next value from the
    iterable.

    Example: To sum a given list,
    ```
    Reduce(lambda acc, i: acc + i).bend([1, 4, 6])  # -> 11
    ```
    """

    def op(self, func, vals):
        try:
            return reduce(func, vals)
        except TypeError as e:  # empty list with no initial value
            raise ValueError(e.args[0])


class Filter(ListOp):
    """
    Similar to Python's filter().
    Builds a new list with the elements of the iterable for which the given
    function returns True.

    Example:
    ```
    Filter(lambda i: i % 2 == 0).bend(range(5))  # -> [0, 2, 4]
    ```
    """

    def op(self, func, vals):
        return list(filter(func, vals))


class FlatForall(ListOp):
    """
    Similar to Forall, but the given function must return an iterable for each
    element of the iterable, which are than "flattened" into a single
    list.

    Example:
    ```
    FlatForall(lambda x: [x-1, x+1]).bend([1, 10, 100])  ->
         [[0, 2], [9, 11], [99, 101]] ->
         [0, 1, 9, 11, 99, 101]
    ```
    """

    def op(self, func, vals):
        return list(chain.from_iterable(map(func, vals)))
