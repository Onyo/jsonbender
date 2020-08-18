from jsonbender.core import bend, Transport
from jsonbender.list_ops import ListOp


class ForallDict(ListOp):
    """
    Maps a dictionary into a list by applying the given function to each key, value pair
    of the dictionary items.

    Example:
    ```
    ForallDict(lambda v: v[0] + v[1])({'a':'b', 'c':'d'})  # -> ['ab','cd']
    ```
    """

    def op(self, func, vals):
        """
        Applies func to each item contained in vals

        :param func: Function which accepts a tuple of (key, value) from the dict
        :param vals: Dictionary that needs to be operated on
        :return: List of mapped dictionary items
        """
        return list(map(func, vals.items()))

    @classmethod
    def bend(cls, mapping, context=None):
        """
        Return a ForallBendDict instance that bends each element of the dictionary
         with the given mapping.

        mapping: a JSONBender mapping as passed to the `bend()` function.
        context: optional. the context that will be passed to `bend()`.
                 Note that if context is not passed, it defaults at bend-time
                 to the one passed to the outer mapping.

        Example:
        ```
        source = {'a':{'b': 1}, 'c': {'b': 2}}
        bender = ForallDict.bend({'b2': Second() >> S('b'), 'identifier': First()})
        bender(source)  # -> [{'b2': 1, 'identifier': 'a'}, {'b2': 2, 'identifier': 'c'}]
        ```

        """
        return ForallBendDict(mapping, context)


class ForallBendDict(ForallDict):
    """
    Bends each item in the dictionary with given mapping and context.

    mapping: a JSONBender mapping as passed to the `bend()` function.
    context: optional. the context that will be passed to `bend()`.
             Note that if context is not passed, it defaults at bend-time
             to the one passed to the outer mapping.
    """

    def __init__(self, mapping, context=None):
        self._mapping = mapping
        self._context = context
        # TODO this is here for retrocompatibility reasons.
        # remove this when ListOp also breaks retrocompatibility
        self._bender = None

    def raw_execute(self, source):
        transport = Transport.from_source(source)
        context = self._context or transport.context
        # ListOp.execute assumes the func is saved on self._func
        self._func = lambda v: bend(self._mapping, v, context)
        return Transport(self.execute(transport.value), transport.context)
