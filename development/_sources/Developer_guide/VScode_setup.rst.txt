################
VS code setup
################

I (KvA) personally really prefer working with VS code, as it has support for basically all different files used in this project. Here, a quick overview for all the changes/additions/settings/etc I have in my own VS code environment.



*********************************
Basic settings changed
*********************************

Vertical rulers
================
You can't go without these when working on files with a line length limit (like python code). Add the ruler through adding the following lines to your environments 'settings.json' file:
.. code-block::

    "editor.rulers": [72, 79],

In my case, the 72 ruler is for python docstrings, the 79 for general (python) code.


Colors
========
I really like my color scheme. My default scheme is default dark plus:
.. code-block::

    "workbench.colorTheme": "Default Dark+",
    "workbench.preferredDarkColorTheme": "Default Dark+",

Besides this, I've changed the color of the multi-line docstring to be slightly darker than the default comment color (I was used to comment-colored docstrings as opposed to string-colored docstrings), while the python comments are a lighter color green. This allows me to easily see the difference between strings, docstrings and colors. These colors are ONLY changed for python, any other file is untouched.

I forgot which, but there is a shortcut key you can press to investigate any color your cursor is hoovering over, to see what its name is (to add in this list), what it's current color is, and how much that color contrasts the current background.
.. code-block::

    "editor.tokenColorCustomizations": {
        "textMateRules": [
            {
                "scope": [
                    "string.quoted.docstring.multi.python",
                    "string.quoted.docstring.raw.multi.python"
                ],
                "settings": {
                    "foreground": "#5e9943" // default: 6A9955
                }
            },
            {
                "scope":"string.quoted.single.python",
                "settings": {
                    "foreground": "#CE9178" // default: CE9178
                }
            },
            {
                "scope": "comment.line.number-sign.python",
                "settings": {
                    "foreground": "#9ccb87"  // default: 6A9955
                }
            }
        ]
    },


Other settings
===============
I personally prefer having word wrap on:
.. code-block::

    "editor.wordWrap": "on",


Zooming out slightly allows me (on my specific, full HD, 1920p screen) to have two 79-char windows side-by-side, along with a useful side-column for file navigation:
.. code-block::

    "window.zoomLevel": -1,


As well as disabling all kinds of fancy, automagic features I don't use:
.. code-block::

    "editor.detectIndentation": false,
    "cSpell.enabled": false,
    "telemetry.telemetryLevel": "off",
    "python.analysis.autoFormatStrings": true,
    "python.analysis.ignore": ["*"],
    "git.decorations.enabled": false,
    


*********************************
Extensions used
*********************************

Python
========
An extension by microsoft to add basic features for python code development. Also installed pylance and python debugger (I believe these were dependencies).

Flake8
=========
An extension by microsoft to add the flake8 linter for python to VScode. I personally prefer this linter over other options.

C/C++
=======
An extension by microsoft to add basic features for c-code development (linting, for example)

reStructuredText Syntax Highlighting
=======================================
An extension by Trond Snekvik that makes rst files somewhat easier to navigate. Among other things allows to navigate the file using the VScode outline feature.

region folding for VS code
===========================
An extension by Maptz that allows you to add comments to any document that mark where the code should be folded. Incredibly useful for file formats that can't be folded by default (like restructuredtext). After installing the extension, the following fragment should be added to your environments 'settings.json' file:
.. code-block::
    
    "restructuredtext.linter.run": "off",
    "maptz.regionfolder": {
    "[restructuredtext]": {  //Language selector
        //Text inserted at the start of the fold. Use the `[NAME]` placeholder
        //to indicate where the cursor should be placed after insertion
        "foldStart": ".. #region [NAME]",

        //Text inserted at the end of the fold
        "foldEnd": ".. #endregion",

        //Regex used to find fold start text.
        "foldStartRegex": "^[\\s]*\\.\\.[\\s]*#region[\\s]*.*[\\s]*$",

        //Regex used to find fold end text.
        "foldEndRegex": "^[\\s]*\\.\\.[\\s]*#endregion[\\s]*$",

        //Turn off #region folding for this language
        "disableFolding": false
    }
    }

Jupyter (optional)
====================
Made by microsoft. Allows me to work with jupyter notebooks. Don't use it very often, but sometimes very nice to have.

Remote - SSH (optional)
========================
Made by microsoft. Used this for a while to directly edit code on clusters.

Live Share (optional)
======================
Also made by microsoft. A very nifty tool that requires the most bananas access to everything (makes sense considering the purpose). If granted, however, this allows you to invite very specific users/machines to your machine. That person can then work on your local copies of files, open terminals/command prompts on your machine with your pre-installed python environments, and more. This basically feels (and looks) how editing a google-docs file with multiple people feels.

Yes, giving this access is scary, make sure you trust the other. Luckily, you can exactly see who's currently connected, and allows to kick/disconnect them. You can use passwords, and more.


