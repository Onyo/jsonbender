About
---

[![Build Status](https://travis-ci.com/Onyo/jsonbender.svg?branch=develop)](https://travis-ci.com/Onyo/jsonbender)

JSONBender is an embedded Python [DSL](https://en.wikipedia.org/wiki/Domain-specific_language) for transforming dicts.
It's name is inspired by Nickelodeon's cartoon series [Avatar: The Last Airbender](https://en.wikipedia.org/wiki/Avatar:_The_Last_Airbender).

![aang](aang.png)


License
---

JSONBender is licensed under the [MIT license](https://choosealicense.com/licenses/mit/). See the LICENSE file for more details.


Installing
---

```bash
pip install JSONBender
```

Contributing
---

If you want to contribute to JSONBender (thanks!), here's how to do it:

1. Fork the repository.
2. Make sure the tests are all fine. Since we support both python 2 and 3, run the tests with [tox](https://github.com/tox-dev/tox):
```bash
tox tests
```
3. Open the pull request!


Usage
---

JSONBender works by calling the `bend()` function with a mapping and the source `dict` as arguments. It raises a `BendingException` if anyting bad happens during the transformation phase.

The mapping itself is a dict whose values are benders, i.e. objects that represent the transformations to be done to the source dict. Ex:

```python
import json

from jsonbender import bend, K, S


MAPPING = {
    'fullName': (S('customer', 'first_name') +
                 K(' ') +
                 S('customer', 'last_name')),
    'city': S('address', 'city'),
}

source = {
    'customer': {
        'first_name': 'Inigo',
        'last_name': 'Montoya',
        'Age': 24,
    },
    'address': {
        'city': 'Sicily',
        'country': 'Florin',
    },
}

result = bend(MAPPING, source)
print(json.dumps(result))
```
```json
{"city": "Sicily", "fullName": "Inigo Montoya"}
```


### Benders


#### Selectors

##### K

`K()` is a selector for constant values:
It takes any value as a parameter and always returns that value regardless of the input.


##### S

`S()` is a selector for accessing keys and indices: It takes a variable number of keys / indices and returns the corresponding value on the source dict:

```python
from jsonbender import bend, S

MAPPING = {'val': S('a', 'deeply', 'nested', 0, 'value')}
ret = bend(MAPPING, {'a': {'deeply': {'nested': [{'value': 42}]}}})
assert ret == {'val': 42}
```

If any of keys may not exist, `S()` can be "annotated" by calling the `.optional(default)` method, which returns an instance of `OptionalS`.
`.optional()` takes a single parameter which is passed as the `default` value of `OptionalS`; it defaults to `None`.

##### OptionalS

`OptionalS` is like `S()` but does not raise errors when any of the keys is not found. Instead, it returns `None` or the `default` value that is passed on its construction.

```python
from jsonbender import bend, OptionalS

source = {'does': {'exist': 23}}

MAPPING_1 = {'val': OptionalS('does', 'not', 'exist')}
ret = bend(MAPPING_1, source)
assert ret == {'val': None}

MAPPING_2 = {'val': OptionalS('does', 'not', 'exist', default=27)}
ret = bend(MAPPING_2, source)
assert ret == {'val': 27}
```

For readability and reusability, prefer using `S().optional()` instead.


##### F
`F()` lifts a python callable into a Bender, so it can be called at bending time.
It is useful for performing more complex operations for which actual python code is necessary.

The extra optional args and kwargs are passed to the function at
bending time after the given value.

```python
from jsonbender import bend, F, S

MAPPING = {
    'total_number_of_keys': F(len),
    'number_of_str_keys': F(lambda source: len([k for k in source.keys()
                                                if isinstance(k, str)])),
    'price_truncated': S('price_as_str') >> F(float) >> F(int),
}
ret = bend(MAPPING, {'price_as_str': '42.2', 'k1': 'v', 1: 'a'})
assert ret == {'price_truncated': 42,
               'total_number_of_keys': 3,
               'number_of_str_keys': 2}
```

If the function can't take certain values, you can protect it by calling the `.protect()` method.

```python
import math
from jsonbender import bend, F, S

MAPPING_1 = {'sqrt': S('val') >> F(math.sqrt).protect()}
assert bend(MAPPING_1, {'val': 4}) == {'sqrt': 2}
assert bend(MAPPING_1, {'val': None}) == {'sqrt': None}

MAPPING_2 = {'sqrt': S('val') >> F(math.sqrt).protect(-1)}
assert bend(MAPPING_2, {'val': -1}) == {'sqrt': -1}
```


#### Operators

Benders implement most of python's binary operators.

##### Arithmetic

For the arithmetic `+`, `-`, `*`, `/`,
the behavior is to apply the operator to the bended values of each operand.

```python
from jsonbender import bend, K, S

a = S('a')
b = S('b')
MAPPING = {'add': a + b, 'sub': a - b, 'mul': a * b, 'div': a / b}
ret = bend(MAPPING, {'a': 10, 'b': 5})
assert ret == {'add': 15, 'sub': 5, 'mul': 50, 'div': 2}

ret = bend({'full_name': S('first_name') + K(' ') + S('last_name')},
           {'first_name': 'John', 'last_name': 'Doe'})
assert ret == {'full_name': 'John Doe'}
```

##### Bitwise

The bitwise operators are not yet implemented, except for the lshift (`<<`) and rshift (`>>`).
See "Composition" below.


#### List ops 

There are 4 benders for working with lists, inspired by the common functional programming operations.

##### Reduce

Similar to Python's `reduce()`.
Reduces an iterable into a single value by repeatedly applying the given
function to the elements.
The function must accept two parameters: the first is the accumulator (the
value returned from the last call), which defaults to the first element of
the iterable (it must be nonempty); the second is the next value from the
iterable.


```python
from jsonbender import bend, Reduce, S

MAPPING = {'sum': S('ints') >> Reduce(lambda acc, i: acc + i)}
ret = bend(MAPPING, {'ints': [1, 4, 7, 9]})
assert ret == {'sum': 21}
```

##### Filter

Similar to Python's `filter()`.
Builds a new list with the elements of the iterable for which the given
function returns True.

```python
from jsonbender import bend, Filter, S

MAPPING = {'even': S('ints') >> Filter(lambda i: i % 2 == 0)}
ret = bend(MAPPING, {'ints': range(5)})
assert ret == {'even': [0, 2, 4]}
```

##### Forall

Similar to Python's `map()`.
Builds a new list by applying the given function to each element of the
iterable.


```python
from jsonbender import bend, Forall, S

MAPPING = {'doubles': S('ints') >> Forall(lambda i: i * 2)}
ret = bend(MAPPING, {'ints': range(5)})
assert ret == {'doubles': [0, 2, 4, 6, 8]}
```

For the common case of applying a JSONBender mapping to each element of a list,
the `.bend()` *class method* is provided, which returns a `ForallBend` instance
. `.bend()` takes the mapping and the context (optional) which are then passed
to `ForallBend`.


##### ForallBend
Bends each element of the list with given mapping and context.

If no context is passed, it "inherits" at bend-time the context passed to the outer `bend()` call.


```python
from jsonbender import bend, S
from jsonbender.list_ops import ForallBend

MAPPING = {'list_of_bs': S('list_of_as') >> ForallBend({'b': S('a')})}
source = {'list_of_as': [{'a': 23}, {'a': 27}]}
ret = bend(MAPPING, source)
assert ret == {'list_of_bs': [{'b': 23}, {'b': 27}]}
```

##### FlatForall

Similar to Forall, but the given function must return an iterable for each
element of the iterable, which are than "flattened" into a single
list.

```python
from jsonbender import bend, S
from jsonbender.list_ops import FlatForall

MAPPING = {'doubles_triples': S('ints') >> FlatForall(lambda x: [x * 2, x * 3])}
source = {'ints': [2, 15, 50]}
ret = bend(MAPPING, source)
assert ret == {'doubles_triples': [4, 6, 30, 45, 100, 150]}
```

#### Control Flow

Sometimes what bender to use must be decided at bending time,
so JSONBender provides 3 control flow structures:


##### Alternation

Take any number of benders, and return the value of the first one that
doesn't raise a LookupError (KeyError, IndexError etc.).

If all benders raise LookupError, re-raise the last raised exception.

```python
from jsonbender import S
from jsonbender.control_flow import Alternation

b = Alternation(S(1), S(0), S('key1'))

b(['a', 'b'])  #  -> 'b'
b(['a'])  #  -> 'a'
try:
    b([])  #  -> TypeError
except TypeError:
    pass

try:
    b({})  #  -> KeyError
except KeyError:
    pass

b({'key1': 23})  # -> 23
```

##### If

Takes a condition bender, and two benders (both default to K(None)).
If the condition bender evaluates to true, return the value of the first
bender. If it evaluates to false, return the value of the second bender.

```python
from jsonbender import K, S
from jsonbender.control_flow import If

if_ = If(S('country') == K('China'), S('first_name'), S('last_name'))
if_({'country': 'China',
     'first_name': 'Li',
     'last_name': 'Na'})  # ->  'Li'

if_({'country': 'Brazil',
     'first_name': 'Gustavo',
     'last_name': 'Kuerten'})  # -> 'Kuerten'
```

##### Switch

Take a key bender, a 'case' container of benders and a default bender
(optional).

The value returned by the key bender is used to get a bender from the
case container, which then returns the result.

If the key is not in the case container, the default is used.

If it's unavailable, raise the original LookupError.

```python
from jsonbender import K, S
from jsonbender.control_flow import Switch

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

#### String ops

JSONBender currently provides only one string-related bender.

##### Format

Return a formatted string just like `str.format()`.
Where the values to be formatted are given by benders as positional or
named parameters.

It uses the same syntax as `str.format()`

```python
from jsonbender import bend, Format, S

MAPPING = {'formatted': Format('{} {} {last}',
                               S('first'),
                               S('second'),
                               last=S('last'))}
source = {'first': 'Edsger', 'second': 'W.', 'last': 'Dijkstra'}
ret = bend(MAPPING, source)
assert ret == {'formatted': 'Edsger W. Dijkstra'}
```


### Composition

All JSONBenders can be composed with other benders using `<<` and `>>`
to make them receive previously bended values.

```python
from jsonbender import bend, F, S
from jsonbender.list_ops import Forall

MAPPING = {
    'name': S('name'),
    'pythonista': S('prog_langs') >> Forall(str.lower) >> F(lambda ls: 'python' in ls),
}
source = {
    'name': 'Mary',
    'prog_langs': ['C', 'Python', 'Lua'],
}
ret = bend(MAPPING, source)
assert ret == {'name': 'Mary', 'pythonista': True}
```

### Context

Sometimes it's necessary to use values at bending time that are not on the
source json and are not known at mapping time.
For these cases there is the optional `context` argument to `bend()` function.
Whatever you pass for the argument is can be used at bending time by the
`Context()` bender.


```python
from jsonbender import bend, Context, S

MAPPING = {
    'name': S('name'),
    'age': (Context() >> S('year')) - S('birthyear'),
}
source = {'name': 'Mary', 'birthyear': 1990}
ret = bend(MAPPING, source, context={'year': 2016})
assert ret == {'name': 'Mary', 'age': 26}
```

