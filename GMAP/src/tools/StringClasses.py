
# local imports
import GMAP.src.tools.Exceptions as GM_Ex
import GMAP.src.tools.MathFunctions as GM_MF
import GMAP.src.tools.PrintTools as GM_PT


class ErrCode(str):
    """Allows for easy comparion of error codes.

    Each warning/error has its own error code. The goal of this class is
    to make it easy to compare them: we want to be able to equate codes
    with wildcards!
    """

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
            GM_PT.Printer().warning(
                f"\n{self} is assumed to be an error code, but does not have "
                "3 parts separated by underscores. Please make sure to only "
                "compare valid error codes.",
                "CT_EC_2",  True, GMAPerrclass=GM_Ex.GmapValueError
            )

        if not isinstance(other, str):
            GM_PT.Printer().warning(
                f"\n{other} is assumed to be an error code, but is not a "
                "string, so this method cannot be used. Please make sure to "
                "only compare strings or ErrCodes.",
                "CT_EC_1",  True, GMAPerrclass=GM_Ex.GmapTypeError
            )
        othersplit = other.split("_")
        if len(othersplit) != 3:
            GM_PT.Printer().warning(
                f"\n{other} is assumed to be an error code, but does not have "
                "3 parts separated by underscores. Please make sure to only "
                "compare valid error codes.",
                "CT_EC_2",  True, GMAPerrclass=GM_Ex.GmapValueError
            )

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


class ColStr(str):
    """Just like normal strings, but additional methods for colors.

    If any string is added to this class (either from the left or from
    the right), the result will be of this class. Similarly, many other
    str operations are possible with this class. When properly
    supported, they will return a ColStr, not 'normal' str.

    So, what's the difference? Consider the following string:
    ``Hello \033[35;1m pretty \033[0m world``
    It contains two ANSI sequences. In this case, they indicate that the
    word 'pretty' should be printed in bright magenta, whereas 'Hello'
    and 'world' should be printed in 'default' colors. As a normal
    python string, it contains 31 characters: all the letters, and all
    the characters of the ANSI codes (the 033 thing is a single
    character). So, its length is 31, and the for-loop iterating through
    it will have 31 iterations. However, when printed to the command
    line, it will only take up 20 characters.

    When dealing with prints, it is very nice to deal with the length
    of the string as observed in the command line. All the functions
    of this class work that way, or are designed to return an instance
    of ColStr, instead of str.

    Currently supported methods:
        __add__, __radd__, __getitem__ (slicing/indexing), __iter__ (for
        item in, list(ColStr)), __len__, __mul__, __rmul__, join,
        replace, split

    .. warning ::
        str.join([ColStr]) will result in a str object, not ColStr!

    .. warning ::
        The color markers are 'attached' to the following character (if
        there is any). If that character is sliced out, the color will
        disappear. If this behaviour poses an issue, open an issue for
        it on github!
    """

    def __add__(self, other):
        return ColStr(super().__add__(other))

    def __radd__(self, other):
        return ColStr(other) + self

    def __getitem__(self, key):
        if isinstance(key, int):  # indexing
            if key >= len(self):
                raise GM_Ex.GmapIndexError
            key = (key, key + 1, 1)
            return ColStr("").join([*self._forwards_generator(key)])

        elif isinstance(key, slice):  # slicing
            key = key.indices(len(self))  # makes sure start and stop >= 0
            if key[2] > 0:
                return ColStr("").join([*self._forwards_generator(key)])
            else:
                # Haven't implemented backwards yet, as it might make less
                # sense for colored strings. Multiple options:
                # - Same as forward, match color with character -> colors get
                #   funky
                # - For each character, identify intended color, and make sure
                #   those are preserved -> actual sequence changes
                # - Omit colors and just revert the 'white' string.

                # key = (key[1], key[0], -1 * key[2])
                raise GM_Ex.GmapNotImplementedError

    def __iter__(self):
        return self._forwards_generator((0, len(self), 1))

    def __len__(self):
        return len(str(self.change_color("white_str")))

    def __mul__(self, other):
        return ColStr(super().__mul__(other))

    def __rmul__(self, other):
        return ColStr(super().__mul__(other))

    def _forwards_generator(self, key):
        """A generator in the forwards direction.

        This is the backbone of __iter__ and __getitem__ -> this is the
        actual mechanism of stepping through the string. Due to the
        logic of recognizing color markers, this exact function only
        works forwards, not backwards. See comments of the __getitem__
        method for more info on backwards.

        Parameters
        ----------
        key : tuple
            This tuple contains three integers: start, stop (exclusive)
            and step. Due to the creation of key, start and stop are
            always positive integers. If a negative-based slice was
            requested, the form was already changed to positive integers
            before being fed here.

        Returns
        -------
        char : `ColStr`
            The next character in the sequence. When printed to the
            terminal, it will appear to have a length of 1 (could also
            be a newline character), but len(str(char)) might not be 1:
            it could contain an ANSI color marker!
        """

        col_ix = 0
        within_col = False
        col_end = ""
        tempstr = ""

        for item in str(self):  # loop over all characters
            # Stop if we went past endpoint
            if col_ix >= key[1]:
                break

            # within color marker? skip through!
            if within_col:  # add item to bin, check if still going
                if len(tempstr) == 1:
                    col_end = "m" if item == "[" else ">"
                tempstr += item
                if item == col_end:
                    within_col = False
                continue

            # start of color marker!
            if item == "\033":  # found a new color
                within_col = True
                tempstr += item
                continue

            # now, a non-color character!
            if len(tempstr) != 0:  # if prev was a color, add it!
                item = tempstr + item
                col_end = ""
                tempstr = ""

            # must it be reported?
            if col_ix < key[0]:  # if its too small/soon
                pass
            elif col_ix == key[0]:
                yield item
            # key[0] < item < key[1], and at step.
            elif (col_ix - key[0]) % key[2] == 0:
                yield item
            col_ix += 1

    def join(self, iterable):
        """A replacement for str.join().

        Uses the super() method, but changes the result back to a ColStr
        object.
        """

        return ColStr(super().join(iterable))

    def replace(self, *args, **kwargs):
        """A replacement for str.replace().

        Uses the super() method, but changes the result back to a ColStr
        object.
        """

        return ColStr(super().replace(*args, **kwargs))

    def split(self, *args, **kwargs):
        """A replacement for str.split().

        Uses the super() method, but changes the result back to a ColStr
        object.
        """

        return [ColStr(item) for item in super().split(*args, **kwargs)]

    def wrap(self, deslen):
        """A shortcut to :func:`~GMAP.src.tools.PrintTools.word_wrap`

        Applies the word_wrap function to itself and returns the result.

        Parameters
        ----------
        deslen : int
            The desired length of the string. Using a greedy algorithm,
            line breaks are inserted to maintain the maximum line
            length.

        Returns
        -------
        wrapped : ColStr
            The same as the input string, but with newlines inserted to
            maintain the maximum line length.
        """

        # word wrap retains type
        return GM_PT.word_wrap(self, deslen=deslen)

    def change_color(self, target_mode):
        """Changes its own color, returns a copy with changed color

        There are different types of colors: internal colors, ANSI
        24bit, ANSI 4bit, and omitting all color. When this function is
        called, any internals present are first converted to 24bit.
        Then, all colors are converted to target_mode.

        Internal colors: We want to be able to give all prints from the
        program a color, even the first. However, at that point in the
        program, we don't yet know whether to print in dark, or light
        mode. Internal colors work with color names which are converted
        to actual ANSI strings when this function runs.

        24bit colors: each color has a rgb code. This is the default of
        the program (all colors are defined that way), and allows for
        the prettiest output.

        4bit colors: These are so old, any hardware imaginable should
        support them. Their larger contrast (as there are so few) should
        also help vision-impaired folks.

        no color: all color markers are removed. Quite useful for when
        writing to the log file.

        Parameters
        ----------
        target_mode : str
            Either '24bit', '4bit' or 'white'. The kind of colors you
            want to see.

        Returns
        -------
        output : str
            The same string as the input one, but with the color markers
            changed to the desired output, or removed altogether.
        """

        # The code should be able to choose the color scheme last-minute, so
        # there are internal codes, too! Here, we switch from internal to ANSI
        # Even if there are no custom markers, don't quit, there might be ANSI
        # markers still!
        colstr = self
        colstr_split = self.split("\033<")
        if len(colstr_split) != 1:  # custom color marker!
            string_list = [item.split(">", 1) for item in colstr_split]
            newlist = [">".join(string_list[0])]  # the '>' isn't color-closing
            for item in string_list[1:]:
                newlist.append(getattr(
                    GM_PT.Printer()._colors, item[0]) + item[1])
            colstr = ColStr("").join(newlist)

        # If we want 24bit, we can stay with the current ANSI codes.
        if target_mode == "24bit":
            return colstr

        # make sure the beginning text has a color, too (just for code
        # simplification, not actually in output)
        colstr_split = colstr.split("\033[")
        if len(colstr_split) == 1:  # no color marker!
            return colstr

        # prepare the string - split it up into a list in which each item
        # represents a monocolor segment. The item is a list of length 2, first
        # the ansi color string, then the actual string.
        newstr = "0m" + colstr
        colstr_split = newstr.split("\033[")
        # cut only at first m as thats the end of the color marker
        colstr_list = [item.split("m", 1) for item in colstr_split]

        # now, change the color of each monocolor substring
        if target_mode == "4bit":  # 8 colors + their bright varieties
            output = colstr_list[0][1]  # don't keep color of first item
            for item in colstr_list[1:]:
                col = self.ANSI24_to_ANSI4(item[0])
                output += f"\033[{col}m{item[1]}"
        elif target_mode == "white_str":  # we need output just for len
            output = "".join([item[1] for item in colstr_list])
        else:  # target_mode white
            # just delete any color markers
            output = ColStr("").join([item[1] for item in colstr_list])
        return output

    def ANSI24_to_ANSI4(self, colorstr):  # used by change_color
        """Change a ANSI-24bit color code to the closest 4bit version.

        Input colorstr in ANSI format (e.g. 38;2;45;61;32). Both
        background and foreground colors are treated. For backgrounds,
        the 'bright' bit is never activated (not all terminals support
        it), but it is for foreground.
        """

        warning_msg = "\nInvalid color specification."

        color_split = colorstr.split(";")  # get all useful values
        color_new = []
        while len(color_split) > 0:
            match color_split[0]:
                case "0":  # reset command - no extra's expected
                    color_new.append("0")
                    color_split = color_split[1:]

                case "38":  # foreground - 5 items including this one
                    curr_color = color_split[:5]
                    if len(curr_color) != 5:  # premature end of list
                        GM_PT.Printer().warning(warning_msg, "PT_CC_1", True)

                    new_col, bright = GM_MF.convert_color_24_4(*curr_color[2:])
                    color_new.append(str(30 + new_col))
                    if bright:
                        color_new.append("1")
                    color_split = color_split[5:]

                case "48":  # background - 5 items including this one
                    curr_color = color_split[:5]
                    if len(curr_color) != 5:  # premature end of list
                        GM_PT.Printer().warning(warning_msg, "PT_CC_1", True)

                    new_col = GM_MF.convert_color_24_4(*curr_color[2:])[0]
                    color_new.append(str(40 + new_col))
                    # no bright - a bright background is not possible
                    color_split = color_split[5:]

                case _:
                    GM_PT.Printer().warning(warning_msg, "PT_CC_1", True)

        return ";".join(color_new)

    def repeat_color(self):
        """Makes sure to repeat earlier color codes after line breaks.

        Input strings MUST contain ANSI sequences, any others are
        ignored.
        """

        # If there is no line break, no need to repeat colors
        if "\n" not in self:
            return self

        # Split the string on color markers first.
        colstr_split = self.split("\033[")
        if len(colstr_split) == 1:  # no color marker
            return self

        # the first part can be directly outputted. Because of the
        # implementation of split, it is already of type ColStr. It maintains
        # its type through additions
        outcolstr = colstr_split[0]
        # Check between any two color markers (and after the last)
        for substr in colstr_split[1:]:
            color, text = substr.split("m", 1)  # separate color and message
            # Anytime a newline occurs, repeat the color after it. Also add the
            # color to the beginning of this string (where it was stripped away
            # from)
            color = f"\033[{color}m"
            outcolstr += color + text.replace("\n", f"\n{color}")

        return outcolstr


class Header():
    """Returns a pretty header for distinguishing prints

    The header will be under and/or overlined with the character
    buffer_char. These lines will have the same length as the title,
    plus extra padding if requested.

    Parameters
    ----------
    title : str
        The text that should be within the header.
    padding_char : str
        The character that should be used for padding around the title
    linemode : str, default="ou"
        which lines should(n't) be displayed. Add the letters for the
        elements you do want to display::

            o: A line above the text
            u: A line below the text
            l: A line left of the text
            r: A line right of the text
            c: Corners

    padding : int, default=0
        How much extra space there should be. Over and underlines will
        get longer by twice this amount, the title itself gets this
        amount of whitespaces before and after the text.
    overline_char, underline_car, left_char, right_char : str, \
    default="-"
        The character that should be used for the respective segment
    corner_char : str, default="+"
        The character that should be used for the corners. If a single
        character is provided, all corners get that character. If
        different characters are desired, there must be 4 characters
        in the string: one for the upleft, upright, downleft, downright
        corner respectively.
    alignment : str, default="centered"
        If the title text consists of multiple lines of unequal length,
        decide how these should be aligned. Regardless of choice, the
        character specified using padding_char will be used to increase
        the lengths of shorter lines. The amount of characters specified
        using padding will be added to the lines after they are made of
        equal length.
        "centered" aligns their midpoints, "leftadj" will align their
        left edges, and "rightadj" will align their right ones.
    maxwidth : int, default=79
        How wide the end result is allowed to be, max. If the title
        text is too wide to fit the requirements, it is line-wrapped to
        fit.
    special : dict, default={}
        Any special rules to apply after the header has been generated.
        Thakes the form of a nested dictionary structure:
        special={"u": {"command": {"|": [[2]]}}}

        - The outermost dict has as the key a string indicating what
          line should be altered. Same shorthands as linemode. The value
          of the dictionary is what should be changed about the line
          (here referred to as the 'rules')
        - The rules dict has the commands as keys, and specific
          instructions (another dict) as the values:

          - replace will put the character saved as key in the
            instructions dict at the positions saved in its values:
            if the line is "abcdefg", {"replace": ["V", [[3]]]} will
            result in "abcVefg". Similarly, {"replace": ["VR",
            [[1, 3], [4, 6]]]} will turn "abcdefg" into "aVRdVRg"

    Returns
    -------
    header : str
        The header, ready for printing.

    Attributes
    ----------
    title : `ColStr` or list of `ColStr`
        The text to be displayed in the header. At the start of __init__
        this is a ColStr, and gets converted to a list of ColStr during
        execution of __init__.
    header : `ColStr`
        The complete header, including all requested features. This is
        the actual string that the caller most likely will want to
        print.
    s : str
        The output of str(self)
    title_lines : int
        The amount of lines the tile spans
    longest_length : int
        The amount of characters the longest line of the title spans.
    over : `ColStr`
        The overline to put in the header (also contains two upper
        corners if corners have been requested)
    under : `ColStr`
        The underline to put in the header (also contains two lower
        corners if corners have been requested)
    left : list of `ColStr`
        The left border line to put in the header
    right : list of `ColStr`
        The right border line to put in the header
    """

    def __init__(
        self, titletext, padding_char=" ", linemode="ou", padding=0,
        overline_char="-", underline_char="-", left_char="|", right_char="|",
        corner_char="+", alignment="centered", maxwidth=79, color_border=None,
        color_text=None, special=None
    ):
        cols = GM_PT.Printer().colors
        # prepare input
        color_border = cols.green_lc if color_border is None else color_border
        color_text = cols.clear if color_text is None else color_text
        special = {} if special is None else special
        self.title = ColStr(titletext)

        # first, prepare the title displayed in the header
        self.format_title(maxwidth, padding)
        self.align_title(alignment, padding_char)
        # now, self.title is a list of ColStr!!!

        # Then, prepare all lines
        self.make_lines(
            linemode, padding, overline_char, underline_char, left_char,
            right_char, corner_char)
        self.do_specials(special)

        # build final product
        self.header = self.finalize(
            color_border, color_text, padding_char, padding)

        self.s = str(self)

    def __str__(self):
        return str(self.header)

    def format_title(self, maxwidth, n_padding):
        """Prepare the title text for the header

        Provided with the maximum width of the entire header, figures
        out the maximum line length for the text within, and adjusts
        self.title to match. Also saves how many lines it created/found.

        Parameters
        ----------
        maxwidth : int
            How wide the end result is allowed to be, max. If the title
            text is too wide to fit the requirements, it is line-wrapped
            to fit.
        n_padding : int
            How much extra space there should be. Over and underlines
            will get longer by twice this amount, the title itself gets
            this amount of whitespaces before and after the text.
        """

        # line wrapping at the correct places.
        title_width = maxwidth - 2 - (n_padding * 2)  # leave space for header
        self.title = self.title.wrap(title_width)
        self.title_lines = len(self.title.split("\n"))

    def align_title(self, alignment, padding_char):
        """Adds whitespaces to all title lines to make them equal length

        When adding these whitespaces, for each line, it must be decided
        whether to add them to the beginning, end, or both. This
        function can either centre all lines, or left- or right adjust
        them.

        Parameters
        ----------
        alignment : str
            How to vertically align the lines. Can be 'leftadj',
            'rightadj' or 'centered'.
        padding_char : str or `ColStr`
            The character used to make the shortest lines longer.
        """

        # padding and adjusting the lines
        title = self.title.split("\n")
        self.longest_length = max([len(item) for item in title])
        if self.title_lines == 1:
            self.title = title
            return

        # doing it like this instead of python str.centre, rjust, ljust, as
        # those don't take the colors into account correctly!
        new_title = []
        for line in title:
            diff = self.longest_length - len(line)
            match alignment:
                case "centered":
                    pre = diff // 2
                    post = diff - pre
                case "leftadj":
                    pre = 0
                    post = diff
                case "rightadj":
                    pre = diff
                    post = 0
            new_title.append(pre * padding_char + line + post * padding_char)
        self.title = new_title
        return

    def make_lines(
        self, linemode, n_padding, overline_char="-", underline_char="-",
        left_char="|", right_char="|", corner_char="+"
    ):
        """Creates the lines making up the border.

        Parameters
        ----------
        linemode : str, default="ou"
            which lines should(n't) be displayed. Add the letters for
            the elements you do want to display::

                o: A line above the text
                u: A line below the text
                l: A line left of the text
                r: A line right of the text
                c: Corners
        padding : int, default=0
            How much extra space there should be. Over and underlines
            will get longer by twice this amount, the title itself gets
            this amount of whitespaces before and after the text.
        overline_char, underline_car, left_char, right_char : str, \
        default="-"
            The character that should be used for the respective segment
        corner_char : str, default="+"
            The character that should be used for the corners. If a
            single character is provided, all corners get that
            character. If different characters are desired, there must
            be 4 characters in the string: one for the upleft, upright,
            downleft, downright corner respectively.
        """

        ou_length = self.longest_length + n_padding * 2
        corner_char = corner_char * 4  # automatically solves all!

        # overline
        self.over = self.line_overunder(
            overline_char, corner_char[:2], linemode, ou_length, "o")

        # sidelines
        self.left = self.line_sides(left_char, linemode, self.title_lines, "l")
        self.right = self.line_sides(
            left_char, linemode, self.title_lines, "r")

        # underline
        self.under = self.line_overunder(
            underline_char, corner_char[2:4], linemode, ou_length, "u")

    def line_overunder(self, line_char, corner_chars, linemode, length, dir):
        """The logic for creating over and underlines.

        Parameters
        ----------
        line_char : str
            The character that should be used to create the line
        corner_chars : str of length 2
            The two corners that should go at the beginning and end of
            the line, if requested.
        linemode : str
            which lines should(n't) be displayed. Add the letters for
            the elements you do want to display::

                o: A line above the text
                u: A line below the text
                l: A line left of the text
                r: A line right of the text
                c: Corners
        length : int
            How long the line-part of the segment should be.
        dir : str
            What direction the line is being made for. Can be 'o' or
            'u', using the same codes as linemode.

        Returns
        -------
        line : `ColStr`
            The line as should be put above/below the header.
        """

        # Get middle portion (if no overline, but corners, we need whitespace)
        if dir in linemode:
            line = line_char * length
        elif "c" in linemode:
            line = " " * length
        else:
            line = ""

        # add corners!
        if "c" in linemode:
            line = corner_chars[0] + line + corner_chars[1]
        elif dir not in linemode:
            pass  # if the entire line is empty, no need to add vertical spacer
        elif "l" in linemode or "r" in linemode:
            if "l" in linemode:
                line = " " + line
            if "r" in linemode:
                line += " "

        return ColStr(line)

    def line_sides(self, line_char, linemode, length, dir):
        """The logic for creating left and right lines.

        Parameters
        ----------
        line_char : str
            The character that should be used to create the line
        linemode : str
            which lines should(n't) be displayed. Add the letters for
            the elements you do want to display::

                o: A line above the text
                u: A line below the text
                l: A line left of the text
                r: A line right of the text
                c: Corners
        length : int
            How long the line-part of the segment should be.
        dir : str
            What direction the line is being made for. Can be 'l' or
            'r', using the same codes as linemode.

        Returns
        -------
        line : list of `ColStr` or list of str
            The line as should be put above/below the header. Each item
            in the list is what should go on a separate line. Lists
            are needed in the case a line (and the corners) are not
            requested - then we need to have an empty string for that
            line.
        """

        if dir in linemode:
            line = [line_char[0]] * length
        elif "c" in linemode:
            line = [" "] * length
        else:
            line = [""] * length
        return line

    def do_specials(self, special):
        """Apply the requested specials to the created lines.

        This allows to make small edits to the given lines.

        Parameters
        ----------
        special : dict, default={}
            Any special rules to apply after the header has been
            generated. Thakes the form of a nested dictionary structure:
            special={"u": {"command": {"|": [[2]]}}}

            - The outermost dict has as the key a string indicating what
              line should be altered. Same shorthands as linemode. The
              value of the dictionary is what should be changed about
              the line (here referred to as the 'rules')
            - The rules dict has the commands as keys, and specific
              instructions (another dict) as the values:

            - replace will put the character saved as key in the
              instructions dict at the positions saved in its values:
              if the line is "abcdefg", {"replace": ["V", [[3]]]} will
              result in "abcVefg". Similarly, {"replace": ["VR",
              [[1, 3], [4, 6]]]} will turn "abcdefg" into "aVRdVRg"
        """

        shorts = {"o": "over", "u": "under", "l": "left", "r": "right"}

        for lineshort, rules in special.items():
            line = getattr(self, shorts[lineshort])
            for command, instructions in rules.items():
                if command == "replace":
                    line = self.specials_replace(
                        lineshort, instructions, line)
            setattr(self, shorts[lineshort], line)

    def specials_replace(self, lineshort, instructions, line):
        """Executes the specials option 'replace'

        Parameters
        ----------
        lineshort : str
            The shorthand representing what line is currently fed to
            the function - 'o', 'u', 'l', or 'r'
        instructions : dict
            The dict saved in specials for the key 'replace'
        line : str or `ColStr` or list of str
            The line to make edits on.

        Returns
        -------
        line : str or `ColStr` or list of str
            The input line, but with all requested changes made.
        """

        # in case of over/under, type(line) == ColStr.
        # in case of left/right, type(line) == list
        linelen = len(line)
        for char, positions in instructions.items():
            char = ColStr(char)
            charlen = len(char)
            # convert to the correct data type for this line
            if lineshort in "lr":
                char = list(char)

            for pos in positions:
                pos[0] = pos[0] + linelen if pos[0] < 0 else pos[0]
                if len(pos) == 1:  # if we just have starting position, get end
                    pos.append(pos[0] + charlen)
                    usechar = char
                else:
                    pos[1] = pos[1] + linelen if pos[1] < 0 else pos[1]
                    desgap = pos[1] - pos[0]
                    usecharlen = charlen
                    if desgap > charlen:
                        usechar = char * (desgap // charlen + 1)
                        usecharlen = charlen * (desgap // charlen + 1)
                    if desgap < usecharlen:
                        usechar = usechar[:desgap]

                line = line[:pos[0]] + usechar + line[pos[1]:]
        return line

    def finalize(self, color_border, color_text, padding_char, n_padding):
        """Brings all created elements together to form the end result

        Parameters
        ----------
        color_border : `ColStr`
            The color that the border should have
        color_text : `ColStr`
            The color that the text should have
        padding_char : str or `ColStr`
            The character used to add some space between the title
            text and border
        n_padding : int
            How much space should be kept (horizontally) between the
            text and the border
        """

        header = ColStr("")

        # overline
        header += color_border + self.over
        if len(self.over) != 0:  # If we have an upper line, add a line break
            header += "\n"

        # sidelines
        pad = padding_char[0] * n_padding
        for lft, txt, rght in zip(self.left, self.title, self.right):
            header += (
                color_border + lft +  # left border
                color_text + pad + txt + pad +  # text + padding
                color_border + rght + "\n")  # right border

        # underline
        header += color_border + self.under + GM_PT.Printer().colors.clear

        return header
