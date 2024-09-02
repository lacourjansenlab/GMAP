
# standard library imports
# import inspect

# local imports
import GMAP.src.tools.Exceptions as GM_Ex
import GMAP.src.tools.PrintTools as GM_PT


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


class ErrCode(str):
    def __eq__(self, other):
        """This is used to see if two error codes equal each other.

        This function exists to quickly check if an error code is
        contained within a container (that should loop and _eq_ each
        item, if I understand correctly).

        One of the error codes can be a string (but not both, because
        in that case this method would not be called).

        Examples
        --------
        >>> errcode = ErrCode("AA_BB_33")

        >>> errcode == "AA_BB_33"
        True
        >>> errcode == "AA_BC_33"
        False

        If one of the two in the comparison is a wildcard (nothing
        specified in that part), that part will always equal. Note the
        double underscore for a wildcard in the middle field:

        >>> errcode == "AA_BB_"
        True
        >>> errcode == "AA_BC_"
        False
        >>> errcode == "AA__33"
        True
        """

        # type checking
        selfsplit = self.split("_")
        if len(selfsplit) != 3:
            self.report_invalid_length(self)

        if not isinstance(other, str):
            self.report_invalid_type(other)
        othersplit = other.split("_")
        if len(othersplit) != 3:
            self.report_invalid_length(other)

        # check the actual equality
        matched = 0
        for selfsub, othersub in zip(selfsplit, othersplit):
            if "" in (selfsub, othersub):
                matched += 1
            elif selfsub == othersub:
                matched += 1

        if matched == 3:
            return True
        else:
            return False

    @staticmethod
    def report_invalid_type(obj):
        """Raises error about obj not being of the correct type.

        The comparisons performed
        """

        GM_PT.Printer().warning(
            f"\n{obj} is assumed to be an error code, but is not a string, "
            "so this method cannot be used. Please make sure to only "
            "compare strings or ErrCodes.",
            "CT_EC_1",  True, GMAPerrclass=GM_Ex.GmapTypeError
        )

    @staticmethod
    def report_invalid_length(obj):
        GM_PT.Printer().warning(
            f"\n{obj} is assumed to be an error code, but does not have 3 "
            "parts separated by underscores. Please make sure to only "
            "compare valid error codes.",
            "CT_EC_2",  True, GMAPerrclass=GM_Ex.GmapValueError
        )


class CustomClass:
    """Creates a new class with attributes equallying given dict entries

    Of the given dictionary, keys will become the attribute names, the
    values will become the actual stored thing in that attribute.
    """

    def __init__(self, **kwargs):
        for parname, val in kwargs.items():
            setattr(self, parname, val)
        return
