##########
Code Style
##########


    The Zen of Python, by Tim Peters
    
    | Beautiful is better than ugly.
    | Explicit is better than implicit.
    | Simple is better than complex.
    | Complex is better than complicated.
    | Flat is better than nested.
    | Sparse is better than dense.
    | Readability counts.
    | Special cases aren't special enough to break the rules.
    | Although practicality beats purity.
    | Errors should never pass silently.
    | Unless explicitly silenced.
    | In the face of ambiguity, refuse the temptation to guess.
    | There should be one-- and preferably only one --obvious way to do it.
    | Although that way may not be obvious at first unless you're Dutch.
    | Now is better than never.
    | Although never is often better than *right* now.
    | If the implementation is hard to explain, it's a bad idea.
    | If the implementation is easy to explain, it may be a good idea.
    | Namespaces are one honking great idea -- let's do more of those!


In order to have a legible, uniform codebase, there are some rules to which any and all code part of this project must adhere to. This document strives to summarize all of those. While we encourage possible code within maps to adhere to these guidelines too, we understand it might be less feasible.


***********************
General tips and tricks
***********************

- Most of the style guide is a summary of the most common/applicable points from `PEP8 <https://peps.python.org/pep-0008/>`__. The rest are additions to it (hopefully in the same spirit) that are specific for this project, or that should guide towards better practices.
- While The Zen of Python was `included in python <https://peps.python.org/pep-0020/>`__ as a joke, it still has very good advice. PEP8 are the rules of programming, The Zen is the spirit.    
- Using a linter can make it a lot easier to enforce these rules. Personally, I use the flake8 linter with VS Code.
- Don't guess line lengths - most editors support rulers. These are vertical lines indicating certain line lengths.
- When reviewing code for this project, please point out any code that doesn't follow these rules.
- Comments are amazing -- let's do more of those!


*******
Remarks
*******

- This codebase is object oriented. For consistency, functional programming should be avoided.
- **Always** use pathlib over os. The os module is deprecated.
- Not a single map should be left in the 'core' - also holds for amideBB and such.
- Argparse has been considered, but will not be used.


*************
General rules
*************

- Documentation, documentation! When writing code, document all the choices/assumptions/etc you make. If it is too much to immediately document them neatly, use the 'development notes-goals-thoughts.md' file. It has a dump section where you can put them down. Add your initials, so someone else can come remind you later.
- Whenever the function of a piece of code isn't easily discernable, use comments.
- Storage space for code is not the issue. Legibility is more important than how compact a line of code is.
- Don't worry about efficiency/speed of a function if it doesnt take more than 1% of total calculation time. This doesn't mean we should aim for blatantly needlessly expensive code -  'good means good enough'.
- Printing should **always** be done using a custom print command, **never** using python's own ``print()``. Unless, of course, when defining the custom print commands.

  - If you want to report something to the user, the :class:`~GMAP.src.tools.print_tools.Printer` object has the ``print`` method. This method takes care of verbose settings, log files, etc.
  - If you want to report an issue, use the warning method of the :class:`~GMAP.src.tools.print_tools.Printer` object. These can also halt the program if the issue is severe enough.
  - If you just want to print something for testing during development, use the :func:`~GMAP.src.tools.print_tools.devprint` function inside print_tools. Import it at the top of the document as dpr to make it convenient to use.
- When creating strings to be printed, f-strings are the preferred method.


***********
Code layout
***********

- Any document should have the following structure (omit what isn't needed):

  - module docstring
  - 1 blank line
  - \_\_future\_\_ imports
  - 1 blank line
  - module level dunder definitions
  - 1 blank line
  - standard library imports (sorted alphabetically)
  - 1 blank line
  - 3rd party imports (sorted alphabetically)
  - 1 blank line
  - local imports (sorted alphabetically)
  - 1 blank line
  - global/constant definitions
  - **2** blank lines
  - class definitions (2 blank lines between classes, 1 blank line between methods)
  - **2** blank lines
  - function definitions, last of which is main() (2 blank lines between functions)
  - **2** blank lines
  - if \_\_name\_\_ == '\_\_main\_\_'

- Restrict the use of globals wherever possible - most projects wont need them!
- No code outside functions/classes/etc, except for the ``if __name__ == '__main__'`` clause. That one should only contain a call to ``main()``, which does not take arguments.
- 4 spaces per indentation level.
- 79 characters per line, except more loosely formatted text blocks, which take 72 characters per line. These include multi-line comments and docstrings.
- Blank lines should be used (albeit sparingly) to separate code into blocks. Think of it like paragraphs in a text.
- Functions should always have a single purpose, and be written as generally as possible (e.g. def calc_avg(), instead of calc_avg_income() ). Aim for functions of around 15 statements (i.e. lines of code if you didn't have to worry about line length).
- Don’t use too many indentation levels. Within a function, don’t go more than three colons deep! (prevents cramped, tiny code lines).


**************
Variable names
**************

- Names of ‘simple’ variables and functions should be in lowercase, separated using underscores: variable_or_function_name
- Names of (instances of) classes (including exception classes) should have every word capitalized: FileParser
- Names of globals should follow that of ‘simple’ variables – but have an underscore at the start. However, not using globals is always strongly preferred. Example: _unnecessary_evil
- Constants are fully capitalized, using underscores to separate words: SPEED_OF_LIGHT
- Classes: the first argument of an instance method should always be ‘self’, the first argument to class methods should always be ‘cls’
- Avoid single-character variable names
- Ideal variable names are usually 5-20 characters long, indicate the semantic meaning, and, where needed, the datatype used.
- If a variable name is already a built-in, but would be very useful, append the variable name with an underscore.


*******
Imports
*******

- Never import everything from a source (from numpy import \*) – this makes the source of methods used very unclear. Things like ‘import numpy’, ‘import numpy as np’, and ‘from numpy import pi’ are okay.
- For local imports, use absolute imports wherever possible – exception to this are large projects where absolute imports are unwieldy, and relative are more legible
- The module os is deprecated – use pathlib instead.


*************
Documentation
*************

- Module, classes, class (instance) methods and functions take docstrings. All of them! A good function docstring briefly (but clearly) indicates what the function does, lists required (and optional) arguments, their semantic meaning, and datatype, and the same for outputs: for each output, the semantic meaning and datatype.
- In this project, docstrings are written in the numpydoc format.
- Comments should be plenty, but not excessive. Explain why a line (or block) of code is there, what its purpose is, but don’t explain a line is printing something, while the call to print() explains this.
- Always explain magic numbers!
- When commenting on a single line, place comment at the end of the line. First two spaces, then ‘#’, then another space, then text. If the comment is too long, place it above the line of code. The ‘#’ is on the same indentation level as the line of code, and ‘#’ is followed by a space, then text.


*******************
General good advice
*******************

- Files are always opened using ‘with open(fname) as fhand:’ – this prevents you from forgetting to close the file after reading it.
- Don’t store the contents of an entire file in memory (e.g. file.readlines()) – especially when unclear about expected file size. Usually, ‘for line in file’ is the go-to file parsing method.
- Try to read files only once.
- Catch errors, but don’t use try-except clauses excessively: many can be avoided using simple if-checks. When using them, only have very little code inside (make it clear which lines/actions require them), and specifically catch the errors you’re looking for
- No return, ‘return’ and ‘return None’ all do the exact same thing. Sometimes you want to be explicit, sometimes you don’t. 
- Ignore any abovementioned rule (sparingly!) when applying the rule would make code less legible.
