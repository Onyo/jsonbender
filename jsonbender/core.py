class Bender:

    """
    Base bending class. All selectors and transformations should directly or
    indirectly derive from this. Should not be instantiated.

    Whenever a bender is activated (by the bend() function), the bend()
    method is called with the source as it's single argument.
    All bending logic should be there.

    Subclasses must implement __init__() and bend() methods.
    """

    def bend(self, source):
        raise NotImplementedError()

    def __eq__(self, other):
        return Eq(self, other)

    def __ne__(self, other):
        return Ne(self, other)

    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def __invert__(self):
        return Invert(self)

    def __add__(self, other):
        return Add(self, other)

    def __sub__(self, other):
        return Sub(self, other)

    def __mul__(self, other):
        return Mul(self, other)

    def __div__(self, other):
        return Div(self, other)

    def __neg__(self):
        return Neg(self)

    def __truediv__(self, other):
        return Div(self, other)

    def __floordiv__(self, other):
        return Div(self, other)

    def __rshift__(self, other):
        return Compose(self, other)

    def __lshift__(self, other):
        return Compose(other, self)

    def __getitem__(self, index):
        return self >> GetItem(index)


class K(Bender):
    """
    Selects a constant value.
    """

    def __init__(self, value):
        self._val = value

    def bend(self, source):
        return self._val


class List(Bender):
    """Bender wrapper for lists."""

    def __init__(self, list_):
        self.list = [benderify(v) for v in list_]

    def bend(self, source):
        return [v.bend(source) for v in self.list]


class Dict(Bender):
    """Bender wrapper for dicts."""

    def __init__(self, dict_):
        self.dict = {k: benderify(v) for k, v in dict_.items()}

    def bend(self, source):
        res = {}
        for k, v in self.dict.items():
            try:
                res[k] = v.bend(source)
            except Exception as e:
                m = "Error for key {}: {}".format(k, str(e))
                raise BendingException(m) from e
        return res


class GetItem(Bender):
    def __init__(self, index):
        self._index = index

    def bend(self, value):
        return value[self._index]


class Compose(Bender):
    def __init__(self, first, second):
        self._first = benderify(first)
        self._second = benderify(second)

    def bend(self, source):
        return self._second.bend(self._first.bend(source))


class UnaryOperator(Bender):
    """
    Base class for unary bending operators. Should not be directly
    instantiated.

    Whenever a unary op is activated, the op() method is called with the
    *value* (that is, the bender is implicitly activated).

    Subclasses must implement the op() method, which takes one value and
    should return the desired result.
    """

    def __init__(self, bender):
        self.bender = benderify(bender)

    def op(self, v):
        raise NotImplementedError()

    def bend(self, source):
        return self.op(self.bender.bend(source))


class Neg(UnaryOperator):
    def op(self, v):
        return -v


class Invert(UnaryOperator):
    def op(self, v):
        return not v


class BinaryOperator(Bender):
    """
    Base class for binary bending operators. Should not be directly
    instantiated.

    Whenever a bin op is activated, the op() method is called with both
    *values* (that is, the benders are implicitly activated).

    Subclasses must implement the op() method, which takes two values and
    should return the desired result.
    """

    def __init__(self, bender1, bender2):
        self._bender1 = benderify(bender1)
        self._bender2 = benderify(bender2)

    def op(self, v1, v2):
        raise NotImplementedError()

    def bend(self, source):
        return self.op(self._bender1.bend(source), self._bender2.bend(source))


class Add(BinaryOperator):
    def op(self, v1, v2):
        return v1 + v2


class Sub(BinaryOperator):
    def op(self, v1, v2):
        return v1 - v2


class Mul(BinaryOperator):
    def op(self, v1, v2):
        return v1 * v2


class Div(BinaryOperator):
    def op(self, v1, v2):
        return float(v1) / float(v2)


class Eq(BinaryOperator):
    def op(self, v1, v2):
        return v1 == v2


class Ne(BinaryOperator):
    def op(self, v1, v2):
        return v1 != v2


class And(BinaryOperator):
    def op(self, v1, v2):
        return v1 and v2


class Or(BinaryOperator):
    def op(self, v1, v2):
        return v1 or v2


class BendingException(Exception):
    pass


def benderify(mapping):
    """Recursively turn all values in a data-structure into bender objects."""
    if isinstance(mapping, list):
        return List(mapping)

    if isinstance(mapping, dict):
        return Dict(mapping)

    if isinstance(mapping, Bender):
        return mapping

    return K(mapping)


def bend(mapping, source):
    """
    The main bending function.

    mapping: the map of benders
    source: a dict to be bent

    returns a new dict according to the provided map.
    """
    return benderify(mapping).bend(source)
