"""
Contains some abstract objects simplifying further code.

Classes
-------
Singleton
    Metaclassing this class makes any class a singleton.
SingletonProperty
    A class that metaclasses a singleton can use the @SingletonProperty
    decorator to expose an attribute of the instance as if belonging
    to the class.
FrozenDict
    Inherits from python dict, but makes it such that after creation,
    the dict cannot be changed anymore.
CustomClass
    Creates a new class with attributes equallying given dict entries.
    Mainly useful for creating dummy objects during testing.
"""


class Singleton(type):
    """Metaclassing this class makes any class a singleton.

    Examples
    --------

    Singleton behaviour (Everything executed in the same session):

    >>> class MyClass1(metaclass=Singleton):
    >>>     def __init__(self, val=None):
    >>>         self.val = val

    >>> class MyClass2(metaclass=Singleton):
    >>>     def __init__(self, val=None):
    >>>         self.val = val

    >>> MyClass1(1).val
    1
    >>> MyClass1(2).val
    1
    >>> MyClass2(3).val  # Now, instantiate other class.
    3
    >>> Myclass1(4).val
    1
    >>> MyClass2(5).val
    3
    >>> MyClass1().val
    1
    >>> MyClass2().val
    3

    Each of the classes keeps the value it got when it was instantiated.
    As they are singletons, they are only instantiated once, and
    subsequent calls that look like a new instance actually are not.

    The different classes metaclassing this singleton don't influence
    each other.

    Finally, as they are only instantiated once, any subsequent calls
    don't even have to supply the (mandatory) parameters.

    Note for developers: These singletons are confusing to pytest. When
    running tests, make sure that the 'reset_singletons' fixture is
    autoused during the session (runs every function). It should be if
    the tests report they are using conftest.py.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonProperty:
    """Decorator implementation for having @property work on the class
    of a singleton subclass, instead of just an instance.

    While I know it is not needed in the current version of GMAP
    (chaining decorators works in 3.9 and 3.10), I would like to
    slightly futureproof the code by not relying on that (as it is
    removed in 3.10+, and no info yet on whether it will return)

    https://stackoverflow.com/questions/76249636/
    class-properties-in-python-3-11

    Parameters
    ----------
    func : callable
        The function or method that describes the property behavior.
    
    Attributes
    ----------
    fget : callable
        The function or method supplied as func.
    """

    def __init__(self, func):
        self.fget = func

    def __get__(self, instance, owner):
        return self.fget(owner.__call__())


class FrozenDict(dict):
    """Immutable dictionary subclass.

    Attempts to alter this dict will raise a `TypeError`. Values are
    *not* recursively frozen, so it will only work as expected with
    immutable values.

    credit: https://stackoverflow.com/questions/62301911/
    is-there-a-dictionary-like-object-that-is-immutable

    Raises
    ------
    TypeError
        If any of (`__add__`, `__radd__`, `__setitem__`, or `update`)
        is called on an instance.
    """

    def __add__(self, other):
        raise TypeError("You may not alter this dictionary")

    def __radd__(self, other):
        raise TypeError("You may not alter this dictionary")

    def __setitem__(self, key, val):
        raise TypeError("You may not alter this dictionary")

    def update(self, other):
        raise TypeError("You may not alter this dictionary")


class CustomClass:
    """Creates a new class with attributes equallying given dict entries

    Of the given dictionary, keys will become the attribute names, the
    values will become the actual stored thing in that attribute.
    """

    def __init__(self, **kwargs):
        for parname, val in kwargs.items():
            setattr(self, parname, val)
