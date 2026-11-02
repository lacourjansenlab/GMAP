"""
Deals with scientific(!) references.

Classes
-------
Reference
    Represents a single reference to literature. Contains all info that
    is present in the .bib file.

Functions
---------
read_reference_file
    Obtain all references from the provided file.
read_reference_string
    Obtain all references from the provided string.
report_references
    The master function for reporting all references relevant for the
    performed run/calculation.
flatten_iterable
    Part of the reference-reporting. Flattens the data structure.
    Creates a predictable simple iterable.
sort_references
    Part of reference-reporting. Collect all applicable references.
    Only keeps the ones relevant for the calculation.
merge_references
    Part of reference-reporting. Merges all applicable references.
    Checks for duplicates, and removes them without removing
    information.
print_references
    Part of reference-reporting. Does the actual printing.
"""


# local imports
import GMAP.src.tools.exceptions as GM_ex
import GMAP.src.tools.print_tools as GM_pt

from GMAP.src.tools.print_tools import devprint as dpr


class Reference:
    """The representation of a single reference.

    These instances save all information present in the .bib file, and
    can return it with simple formatting.

    Parameters
    ----------
    input_string : str
        The string that contains this specific reference.

    Attributes
    ----------
    input_string : str
        The string provided to the __init__ method. This string can be
        used to later see what was used to instantiate the class (and,
        for example, for creating a copy of the instance).
    dir_attr : list
        A list of strings, each string being a field name. These are the
        fields that can be directly read from the .bib file / input
        string.
    all_attr : list
        A list of strings, each string being a field name (except one).
        These are the ones that make up the entire object, and the ones
        that should be reported when printing. If none of these strings
        are also class attributes, this instance is considered 'failed'.
    success : bool
        Whether this object has been interpreted correctly and can be
        used safely by the program.
    title : str
        The title of the paper/article/book/etc as provided in the
        reference.
    author : list
        A list of strings. Each string is a single author with their
        family name first, then their given name(s). The given name(s)
        is/are abbreviated to (a) single letter(s).
    author_raw : list
        A list of strings. Each string is a single author as directly
        cut from the .bib file. It is assumed the bib file always has
        the family name first, given name second.
    year : str
        The string representation of the year the work was published,
        as provided in the reference.
    month : str
        The string representation of the month the work was published,
        as provided in the reference.
    journal : str
        The name of the journal in which the work was published,
        as provided in the reference.
    volume : str
        The string representation of the volume (usually a number) of
        the edition of the journal in which the work was published,
        as provided in the reference.
    number : str
        The string representation of the issue (usually a number) of
        the edition of the journal in which the work was published,
        as provided in the reference.
    pages : str
        The string representation of the page(s) on which the work was
        published, as provided in the reference.
    issn : str
        The string representation of the issn number of the work, as
        provided in the reference.
    doi : str
        The string representation of the DOI assigned to the work, as
        provided in the reference.
    url : str
        The url through which the work was obtained (and can be
        obtained) as provided in the reference.
    mapkey : list
        A list of strings. Each string is one of the keys mentioned in
        the input string. Distinct keys are separated by a semicolon,
        followed by a whitespace: "; "
    reporttext : dict
        A dict of all ways/reasons to report this reference. The keys
        are the possible outputs the program can generate (currently,
        ham, ene, dip, ram, pos, dbp), the values are the text(s) that
        should be printed for that specific output.

        The input string looks like this:

        "ham, ene: print this for hamiltonian and energies output;
        dip: print this for dipole output"

        A text is placed after its associated outputs, separated by a
        colon. If there are multiple different output/text pairs, those
        are separated using a semicolon. When multiple outputs share
        a text, they are separated using a comma.
    bibtype : str
        The type of bib entry (the very first thing in a bib entry).
    bibkey : str
        The key used by reference managers (between curly braces on the
        first line of a bib entry).
    """

    def __init__(self, input_string):
        self.input_string = input_string

        # read from bib file directly
        self.dir_attr = [
            "title", "year", "month", "journal", "volume", "number", "pages",
            "issn", "doi", "url"]

        # all possible (usable) attributes
        self.all_attr = self.dir_attr[:] + [
            "author_raw", "mapkey", "reporttext"]

        try:
            self.interpret_input_string(input_string)
        except Exception:
            self.success = False
            return

        if (
            not any(hasattr(self, x) for x in self.all_attr)

            # later functions assume these to be present
            or not hasattr(self, "mapkey")
            or not hasattr(self, "reporttext")
        ):
            self.success = False
        else:
            self.success = True

        if hasattr(self, "author_raw"):
            self.format_author()

    def __eq__(self, other):
        return str(self) == str(other)

    def __str__(self):

        outstr = ""  # we're going to build this up

        # Report on author
        if hasattr(self, "author"):
            outstr += self.authorstr() + ". "
        else:
            outstr += "unknown author. "

        # Report on title
        if hasattr(self, "title"):
            outstr += f'"{self.title}". '
        else:
            outstr += "unknown title. "

        # Report on journal name
        outstr += "In "
        outstr += getattr(self, "journal", "unknown journal") + " "

        # Report on journal volume/number
        if hasattr(self, "volume"):
            if hasattr(self, "number"):
                outstr += self.volume + "." + self.number
            else:
                outstr += "vol. " + self.volume
        else:
            if hasattr(self, "number"):
                outstr += "no. " + self.number
            else:
                outstr += ""

        # Report on publication date
        if hasattr(self, "year"):
            if hasattr(self, "month"):
                outstr += f" ({self.month} {self.year})"
            else:
                outstr += f" ({self.year})"
        else:
            outstr += " (unknown year)"

        # Report on page in journal
        if hasattr(self, "pages"):
            if "-" in self.pages:
                outstr += ", pp. " + self.pages
            else:
                outstr += ", p. " + self.pages

        # report other info
        for type in ["issn", "doi", "url"]:
            if hasattr(self, type):
                outstr += ", " + type + ": " + getattr(self, type)

        return outstr

    def interpret_input_string(self, input_string):
        """The core method for parsing the input string provided upon
        initializing this class.

        Parameters
        ----------
        input_string : str
            The string that contains this specific reference.
        """

        # split and parse first line
        attribute_list = input_string.split("\n")
        self.bibtype, self.bibkey = attribute_list[0].rstrip(",").split("{")

        # loop over all .bib fields
        for line in attribute_list[1:]:
            linelist = line.split("=")
            linelist = [item.strip("\t{ },") for item in linelist]

            # the 'simple' bib fields can be written directly
            if linelist[0] in self.dir_attr:
                setattr(self, linelist[0], linelist[1])

            # the author bib field needs some love
            elif linelist[0] == "author":
                self.author_raw = [
                    author.split(", ")
                    for author in linelist[1].split(" and ")]

            # keys that can be used by map authors to quickly identify any
            # references (in case they need to be sorted)
            elif linelist[0] == "mapkey":
                self.mapkey = [key.strip() for key in linelist[1].split("; ")]

            # for each mentioned output, save the text that should be reported
            elif linelist[0] == "reporttext":
                self.reporttext = {}
                for item in linelist[1].split(";"):
                    outputs, text = item.strip().split(":")
                    for output in outputs.strip().split(","):
                        output = output.strip()
                        if output not in self.reporttext:
                            self.reporttext[output] = [text.strip()]
                        else:
                            self.reporttext[output].append(text.strip())

    def format_author(self):
        """Parses the raw author string (as obtained from the reference)
        into the style of GMAP.

        Assumes the family name is mentioned first, and the given
        name(s) come(s) after. Main goal is to shorten all given names
        to a single letter, as to make this equal across all papers.
        Some do already give letters only, others full names.
        """

        self.author = []
        for author in self.author_raw:
            # report only initials, not whole names
            first_letters = [name[0] + "." for name in author[1].split(" ")]
            self.author.append(author[0] + ", " + " ".join(first_letters))

    def authorstr(self):
        """Prepares the author attribute for printing.

        The author attribute has already been formatted to contain only
        initials, now, all names are added together. If there are too
        many names, only report the first 5, and omit the rest.
        """

        # 5 authors has been chosen to be the maximum amount for printing.
        if len(self.author) > 5:
            return "; ".join(self.author[:5]) + " et al"
        else:
            return "; ".join(self.author)


def read_reference_file(fname):
    """Obtain all references from the provided file.

    The references are sorted into the output dict by their mapkey
    fields. If a single reference has multiple map keys, it occurs
    once for each.

    Parameters
    ----------
    fname : `pathlib.Path`
        The name of the file whose contents should be parsed into
        reference objects

    Returns
    -------
    allrefs : dict
        The keys of this dictionary are the individual mapkeys found in
        the references in the files. The values are lists of all
        references that have that specific key in their mapkey field.
    """

    with open(fname, encoding="utf-8") as fhand:
        alldata = fhand.read()
    allrefs = read_reference_string(alldata)
    return allrefs


def read_reference_string(string):
    """Obtain all references from the provided string.

    The string is assumed to look like the contents of a .bib file.

    Parameters
    ----------
    string : str
        The string to parse.

    Returns
    -------
    allrefs : dict
        The keys of this dictionary are the individual mapkeys found in
        the references in the files. The values are lists of all
        references that have that specific key in their mapkey field.
    """

    allrefs = {}
    reflist = string.split("\n@")
    for ref in reflist:
        ref = ref.strip()
        if len(ref) > 0:
            refparse = Reference(ref)
            if refparse.success:
                # save reference under each of its listed keys.
                for key in refparse.mapkey:
                    if key not in allrefs:
                        allrefs[key] = [refparse]
                    else:
                        allrefs[key].append(refparse)

    return allrefs


# above: functions/classes used mainly for reading in the references
# ----------------------------------------------------------------------
# below: functions/classes used for printing/reporting the references


def report_references(run_pars, iterable):
    """Report all references for this calculation.

    This function can be called once, or more often - the result doesn't
    look different (if there are no duplicate references between calls)

    This is the 'master' function. It splits up into 4 separate steps,
    called 'flatten_iterable', 'sort_references', 'merge_references'
    and 'print_references'. This is the rough workflow:

    flatten_iterable
        The input iterable structure can vary. Process it into a
        predictable format.

    sort_references
        Considering the run just performed, keep the references that
        correspond to the calculated output, omit the rest.

    merge_references
        One paper might occur multiple times. Sort through all
        references that should be reported, and remove any duplicates,
        merging the messages corresponding to all instances. This merge
        can happen across reference sources (different maps, for
        example)

    Parameters
    ----------
    run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
        The 'main' RunPars instance containing all the basic
        run-defining parameters.
    iterable : :class:`Reference` or list or dict
        All references that should be used for reporting.
    """

    # obtain GMAP reference
    references_filename = run_pars.references_file

    if references_filename.is_file():
        references = read_reference_file(references_filename)
    else:
        GM_pt.Printer.warning(
            "\nCould not find the GMAP references file. Please don't forget to cite the GMAP paper along with the other references below!",
            "RH_GR_1", False
        )
        references = {}

    # make list of ref objects
    references = flatten_iterable(references) + flatten_iterable(iterable)

    # dpr(*[str(reference) + "\n" for reference in references])

    # list of ref objects with their reporttext (may haveduplicates)
    references = sort_references(run_pars, references)

    # dpr(*references)

    # dict of str(ref obj): list of all reporttext
    references = merge_references(references)

    print_references(references)


def flatten_iterable(iterable):
    """Part of the reference-reporting. Flattens the data structure.

    The target structure is just a simple list of references. No work
    on sorting/grouping references is done.

    Parameters
    ----------
    iterable : :class:`Reference` or list or dict
        All references that should be used for reporting.

    Returns
    -------
    iterable : list of :class:`Reference`
        All references present in the input iterable.
    """

    if isinstance(iterable, dict):
        iterable = [*iterable.values()]
    elif isinstance(iterable, list):
        pass
    elif isinstance(iterable, Reference):
        iterable = [iterable]
    else:
        # we can safely raise here - this should never be encountered by an
        # user, only by developers and map creators
        raise GM_ex.GmapTypeError

    while not all(isinstance(item, Reference) for item in iterable):
        references_list = []
        for item in iterable:
            if isinstance(item, dict):
                references_list.extend(item.values())
            elif isinstance(item, list):
                references_list.extend(item)
            elif isinstance(item, Reference):
                references_list.append(item)
            else:
                # we can safely raise here - this should never be encountered
                # by an user, only by developers and map creators
                raise GM_ex.GmapTypeError
        iterable = references_list[:]

    return iterable


def sort_references(run_pars, references):
    """Part of reference-reporting. Collect all applicable references.

    Not all references have to be printed every calculation. Each
    reference should have a reporttext field. Each time a listed method
    is one of the calculated ones, it's message (together with the
    reference) is added to the returned list.

    The resulting output structure contains a reference with its reason
    to be reported, without further processing.

    Parameters
    ----------
    run_pars : :class:`~GMAP.src.tools.parameter_parser.RunPars`
        The 'main' RunPars instance containing all the basic
        run-defining parameters.
    references : list of :class:`Reference`
        All references present in the input iterable.

    Returns
    -------
    used_references : list of lists of :class:`Reference`, str pairs
        Each of the sublists in the larger list contains first a
        reference, second the reason that reference should be reported.
    """

    used_references = []
    for calc_mode in run_pars.requested_job + run_pars.output_data:
        for reference in references:
            if calc_mode in reference.reporttext:
                for text in reference.reporttext[calc_mode]:
                    used_references.append([reference, text])

    return used_references


def merge_references(references):
    """Part of reference-reporting. Merges all applicable references.

    Until now, there could have been a lot of duplicate references
    floating around. It is time to make sure we gather all instances
    of the same reference, with all the reasons to print it. The goal
    is to make the printed format more human-readable: we list a single
    reference, along with all reasons it should be cited, before moving
    on to the next one.

    Merging is done on a very simple basis: if two :class:`Reference`
    objects have the same string representation, they are considered
    equal. This allows to have the same reference present in multiple
    different files/sources.

    Parameters
    ----------
    references : list of lists of :class:`Reference`, str pairs
        Each of the sublists in the larger list contains first a
        reference, second the reason that reference should be reported.

    Returns
    -------
    unique_references : dict
        The keys are the string representations of the references. The
        values are lists of the reasons for reporting a reference.
    """

    unique_references = {}
    for reference in references:
        reference, reporttext = reference
        refstr = str(reference)
        if refstr in unique_references:
            if reporttext not in unique_references[refstr]:
                unique_references[refstr].append(reporttext)
        else:
            unique_references[refstr] = [reporttext]
    return unique_references


def print_references(references):
    """Part of reference-reporting. Does the actual printing.

    Parameters
    ----------
    references : dict
        The keys are the string representations of the references. The
        values are lists of the reasons for reporting a reference.
    """

    pr = GM_pt.Printer

    for refstr, reporttexts in references.items():
        pr.print(2, "The following reference was used for calculating the:")
        for reporttext in reporttexts:
            pr.print(2, f" - {reporttext}", wrap_preline="   ")
        pr.print(1, f"{refstr}\n")
