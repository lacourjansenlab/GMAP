
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
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
