# GEMAIM-dev

This is the development version of GEMAIM. 

## How to use:
1. Clone this github repo, and navigate to the directory this file is located in.
2. Using ```python -m venv env_GMAP```, create a virtual environment.
3. Activate the environment by running
* (Unix)  ```source env_GMAP/bin/activate```
* (Windows) ```env_GMAP\Scripts\activate.bat``` (doesn't work in powershell)
4. Install GEMAIM:
* (general users) run ```python3 -m pip install .```
* (developers) run ```python3 -m pip install -e ".[testing]"```
5. now, from anywhere, typing ```GMAP``` will start the program!

## How to generate the documentation using sphinx:
Assuming generating from scratch, and inside a venv (see above, always a good habit)
1. When doing this in a different repository (i.e. no automagical module installs), make sure to run ```pip install sphinx```, ```pip install numpydoc```, and (optionally) ```pip install pydata-sphinx-theme```
2. Create a directory for all sphinx output using ```mkdir sphinx```. It is preferred this directory lives in the base directory of your project (in case of GMAP, the same directory as where this document is located).
3. Navigate to the newly created directory. Inside, run ```sphinx-quickstart```. You are prompted to make some choices, but the defaults are good enough. Just keep hitting enter until done. This will create a file named ```conf.py``` and one named ```index.rst```, along with some makefiles. Remember the abovementioned two files, they're important!
4. Make the following changes to the conf.py:
  * At the very top of the file, add the line ```import sys``` and ```from pathlib import Path```
  * a bit further down, replace ```extensions = []``` with ```extensions = ['sphinx.ext.autodoc', 'numpydoc']```
  * just below this, there are definitions for templates_path and exclude_patterns. Just below there, add the following line: ```sys.path.append(str((Path(__file__).parent).resolve()))```
  * **if** you installed the pydata theme earlier, replace the line ```html_theme = 'alabaster'``` line further down in the document with ```html_theme = 'pydata_sphinx_theme'```
5. Within the sphinx output directory, create another directory for the api output using ```mkdir api_out```
6. **Without** changing directories, run ```sphinx-apidoc -o api_out ../GMAP```. When building for a different project, make sure to point to the base folder of the **code** part of your project.
7. Make the following changes to index.rst (you know, that file created in step 3):
  * replace ```:maxdepth: 2``` with ```:maxdepth: 4``` in case your project is very nested like GMAP
  * right below this line, add the line ```:glob:``` - make sure to match the indentation of the lines above!
  * right below the glob line, add an empty line, followed by the line ```api_out/**.rst```. Again, make sure to mind indentation!
8. Within the sphinx output directory, run the following commands:
  * (optional if familiar with output) ```make``` - this will show all supported document types to generate docs. We'll be using basic html here, but note the fact you can also generate a pdf, man file, and many more!
  * Build the documentation of your choice. In case of html, the command will be ```make html```

The ouput files will be inside the sphinx folder, in _build/html. Open _build/html/index.html to get to the home page of your 'website'.

In case you build html documents, the interlinking is relative: you can move (and rename) the 'html' folder to your liking. It can be shared and everything, and it should even be compatible with github pages (if I understand things correctly).

When you've made some choices to the code, and would like to rebuild the docs, not all steps have to be followed again. For minor changes, it is sufficient to redo step 8 only. For major changes (those that involve the addition/removal/restructuring of (sub)modules), restart at step 6.
