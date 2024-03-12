################
Useful resources
################

These resources might come in handy while writing code/documentation for this project.


*********************************
Sources for writing documentation
*********************************

Installation
============
Installing all programs to create the documentation might be confusing. Besides the installation instructions in this project's README.md, you might also want to check out the following resources:

- `Installing sphinx <https://www.sphinx-doc.org/en/master/usage/installation.html>`__ from the Sphinx main documentation pages provides many different ways of installing sphinx besides pip install.
- `Getting started <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>`__ from the numpydoc pages explains how to install it, and gives some possible flags to use in the sphinx conf.py.
- `Napoleon <https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html>`__ is another tool that can be used for reading numpydoc-style docstrings, I haven't used it yet at the time of writing this.
- The `sphinx autodoc tutorial for dummies <https://codeandchaos.wordpress.com/2012/07/30/sphinx-autodoc-tutorial-for-dummies/>`__ might be ancient and written for python 2.7, it still gives a good overview of the steps required. Many details, however, are not accurate anymore.
- `Sphinx and numpydoc <https://codeandchaos.wordpress.com/2012/08/09/sphinx-and-numpydoc/>`__ is the followup to the autodoc tutorial for dummies. Same warnings apply!
- On the `sphinx theme gallery page <https://sphinx-themes.org/>`__ you can find many more themes to render documentation in.
- `Sphinx-design <https://sphinx-design.readthedocs.io/en/latest/get_started.html>`__ allows the use of more complex structures in the pages.


Setting up
==========
After installation, Sphinx needs to be configured. Here are some useful pages on how to configure different parts/tools.

- `Configuration <https://www.sphinx-doc.org/en/master/usage/configuration.html>`__ from the sphinx documentation pages lists many possible options/settings for the sphinx conf.py file.
- `Autodoc <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>`__ is the tool used for automatically retrieving docstrings from python code.
- Sphinx apidoc can take `additional commands <https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html>`__ .


Writing documentation
=====================
At some point the documentation itself has to be written. reST and numpydoc have their own syntax, here are some pages to help with that.

- `Cheat sheets <https://bashtage.github.io/sphinx-material/rst-cheatsheet/rst-cheatsheet.html>`__ are always the best!
- `Directives <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html>`__ automatially create text with a special format. There are many available options - a good example is the 'see also' section that exists on most numpy pages. `Example <https://numpy.org/doc/stable/reference/generated/numpy.mean.html>`__
- Numpydoc has written a cohesive `style guide <https://numpydoc.readthedocs.io/en/latest/format.html>`__ which explains how each section of a docstring should be used, but doesn't explain much on how to actually do many things.
- In addition to the previous point, `sphinx <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html>`__ has some very good examples of docstrings.
- `This <https://stackoverflow.com/questions/21289806/link-to-class-method-in-python-docstring>`__ and `this <https://stackoverflow.com/questions/22700606/how-would-i-cross-reference-a-function-generated-by-autodoc-in-sphinx>`__ stackoverflow question both have some very clear answers on how to link to code objects, both from within docstrings, and in other documentation pages like this one.
- In addition to the previous point, `here <https://www.sphinx-doc.org/en/master/usage/domains/python.html>`__ is an overview on what flags for python objects are available besides those mentioned in the stackoverflow answers.
- General cross-references are explained `here <https://docs.readthedocs.io/en/stable/guides/cross-referencing-with-sphinx.html>`__ , this is mainly useful to linking to pages like this.
- Although a very niche problem, `this solution <https://stackoverflow.com/questions/38347932/bullet-lists-after-paragraph-in-python-docstring-sometimes-dont-work-with-sphin>`__ for when sphinx throws an error related to unordered list within python docstrings. The error text is not very clear, you have to recognize the error by knowing the function that throws the error has an unordered list.
- `This stackoverflow question <https://stackoverflow.com/questions/17189038/generating-an-external-link-in-sphinx>`__ has some useful answers on how to add website hyperlinks in your documentation pages. Or you just check out the source of this page for plenty of examples.
- `This <https://sublime-and-sphinx-guide.readthedocs.io/en/latest/lists.html>`__ is a good explanation on how to use (un)ordered (nested) lists in the documentation pages.
- and `this <https://lpn-doc-sphinx-primer.readthedocs.io/en/stable/concepts/heading.html>`__ is a good example on how to mark headers.
- `The PyData Sphinx Theme <https://pydata-sphinx-theme.readthedocs.io/en/stable/index.html>`__ page contains some cool inspiration for looks/layout/structure of webpage.
- The current home page of the documentation contains a combination of `grids <https://sphinx-design.readthedocs.io/en/latest/grids.html>`__ and `cards <https://sphinx-design.readthedocs.io/en/latest/cards.html>`__ for a cleaner look.



