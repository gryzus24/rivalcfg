"""
This module contains varous helper functions.
"""


import re


def merge_bytes(*args):
    """Returns a single list of int from given int and list of int.

    :param int,list[int] args: Values to merge
    :rtype: list[int]

    >>> from rivalcfg.helpers import merge_bytes
    >>> merge_bytes(1, 2, 3)
    [1, 2, 3]
    >>> merge_bytes([1, 2], [3, 4])
    [1, 2, 3, 4]
    >>> merge_bytes(1, [2, 3], 4)
    [1, 2, 3, 4]
    """
    result = []
    for arg in args:
        if type(arg) in [list, tuple]:
            result.extend(arg)
        else:
            result.append(arg)
    return result


def module_ls(module):
    """List the content of the given Python module, ignoring private elements.

    :param module: The module to list.
    :rtype: [str]
    """
    return [e for e in dir(module) if not e.startswith("_")]


def parse_param_string(paramstr, value_parsers={}):
    """Parses a parameter string (used for rgbgrandiant).

    :param str paramstr: The parameter string.
    :param dict value_parsers: Additional parsers to parse values.
    :rtype: dict

    Example syntax::

       myparam(foo=1; bar=hello; baz=a, b, c)

    Once parsed, it will return this::

       {
           "myparam": {
               "foo": "1",
               "bar": "hello",
               "baz": "a, b, c",
           }
       }

    Additional parsers can be provided to parse the values, see examples
    bellow.

    >>> parse_param_string("hello(name=world)")
    {'hello': {'name': 'world'}}
    >>> parse_param_string("foo(bar=1; baz=2)")
    {'foo': {'bar': '1', 'baz': '2'}}
    >>> parse_param_string("foo(a=42; b=3.14)", value_parsers={
    ...     "foo": {
    ...         "a": int,
    ...         "b": float
    ...     }
    ... })
    {'foo': {'a': 42, 'b': 3.14}}
    >>> parse_param_string("foobar[a=1]")
    Traceback (most recent call last):
        ...
    ValueError: invalid parameter string 'foobar[a=1]'
    """
    regexp_fn = re.compile(r"^\s*([a-zA-Z0-9_]+)\s*\(\s*(.+)\s*\)\s*$")

    if not regexp_fn.match(paramstr):
        raise ValueError("invalid parameter string '%s'" % paramstr)

    name = regexp_fn.match(paramstr).group(1)
    params = regexp_fn.match(paramstr).group(2)

    result = {
            name: {
                k.strip(): v.strip() for k, v in [
                    p.split("=") for p in params.split(";")]
                }
            }

    if value_parsers:
        for key, value in result[name].items():
            if name in value_parsers and key in value_parsers[name]:
                result[name][key] = value_parsers[name][key](value)

    return result


def uint_to_little_endian_bytearray(number, size):
    """Converts an unsigned interger to a little endian bytearray.

    :param in number: The number to convert.
    :param in size: The length of the target bytearray.
    :rtype: [int]

    >>> uint_to_little_endian_bytearray(0x42, 1)
    [66]
    >>> uint_to_little_endian_bytearray(0x42, 2)
    [66, 0]
    >>> uint_to_little_endian_bytearray(0xFF42, 2)
    [66, 255]
    >>> uint_to_little_endian_bytearray(0xFF42, 4)
    [66, 255, 0, 0]
    >>> uint_to_little_endian_bytearray(0xFFFFFF, 2)
    Traceback (most recent call last):
        ...
    ValueError: integer overflow
    """
    if number > (2 ** (8 * size) - 1):
        raise ValueError("integer overflow")
    nle = [0] * size
    for i in range(size):
        nle[i] = number >> i*8 & 0xFF
    return nle
