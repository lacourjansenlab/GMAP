[![Coverage Status](https://raw.githubusercontent.com/lacourjansenlab/GMAP/refs/heads/gh-pages/coverage-badge.svg)](https://raw.githubusercontent.com/lacourjansenlab/GMAP/refs/heads/gh-pages/htmlcov/index.html)

# GMAP

This is the main version of GMAP. Both the stable release version (main branch) and developments (other branches) can be found here.

GMAP is a package of tools for use in computing spectra from molecular dynamics trajectories. Currently, the main tool is GEM, which supports both vibrational and electronic spectroscopy.

[The manual can be found here](https://lacourjansenlab.github.io/GMAP/)


on this page:
- [Where to download](#where-to-download)
- [How to install](#how-to-install-general-users)
- [How to expand the program using maps](#how-to-expand-the-program-using-maps)
- [How to compile C code](#how-to-compile-c-code)
- [Differences between GMAP and AIM](#differences-between-gmap-and-aim)
- [Version information](#version-information)


## Where to download

When downloading GMAP, please download a release. You can either:
- pick the most recent release in the [github releases window](https://github.com/lacourjansenlab/GMAP/releases), where you manually download the .zip archive. Move it to where you want to install GMAP, and unzip.
- pick the most recent release in the [github releases window](https://github.com/lacourjansenlab/GMAP/releases), remember its tag (vx.y.z). Now, use git to get the program local (git clone), and make sure to either clone or checkout the correct branch. For the branch name, use the tag (so vx.y.z, including the 'v').
- In the [download overview](https://lacourjansenlab.github.io/GMAP/stable/#where-to-download-gmap), pick the specific version you are interested in, and follow the link. Here, follow either of the above steps for that specific version.


## How to install 

The installation instructions mention using a venv. This virtual environment is a little like a quarantine for modules. Anything you do in the virtual environment, stays there. So if multiple programs need different versions of the same module, you don't have to keep re-installing that module when switching programs.

While the instructions work without one, it is definitely good practice to use one, so we highly recommend it!

### Installation for general users:
1. Make sure you have a valid python installation. For details, see [Version information](#version-information)
2. [Download or clone](#where-to-download) this github repo, and navigate to the directory **this** file is located in.
3. Using ```python -m venv env_GMAP```, create a virtual environment.
4. Activate the environment by running
   * (Unix)  ```source env_GMAP/bin/activate```
   * (Windows) ```env_GMAP\Scripts\activate.bat``` (doesn't work in powershell)
5. (optional) Don't forget to [compile the GMAP C library!](#how-to-compile-c-code) There are also some maps that might need to have their C libraries installed, they will mention this in their README. Compilation instructions are system dependent, and given lower down in this file. After this installation, the program is ready for use. 

   This step is optional, because compiled versions of all files come with the program. If you'd rather compile yourself than using ours, this is the time to do so!
6. Install GMAP:
   * (general users, use wheel, windows) run ```python3 -m pip install dist\gmap-0.0.1-py3-none-any.whl```
   * (general users, use wheel, unix) run ```python3 -m pip install dist/gmap-0.0.1-py3-none-any.whl```
   * (general users, rebuild wheel) run ```python3 -m pip install .```
   * (developers) run ```python3 -m pip install -e ".[testing]"```
7. now, from anywhere, typing ```GMAP``` will start the program. If not, something has gone wrong. However, we're not done yet.
8. Once you're done using the program, you can deactivate the environment again by typing ```deactivate```.

### Installation for developers
1. Follow steps 1-6 of the non-developer guide.
2. Build your changes before opening a PR. ``pip install build`` if you don't have it yet; then ``python -m build`` (all from repo home directory)
3. only relevant for some developers: If you want to fully profile the code and have GMAP generate the flow-chart-png for you, an installation of [graphvis](https://graphviz.org/) must be present. It is responsible for executing the 'dot' command on the command line. At the moment of writing this, a single test will fail if graphvis is not installed.

### How to use GMAP (after installing)
1. Make sure you installed the program.
2. Activate the environment you created during installation. Activation instructions are in step 3 of the installation instructions.
3. Run the program; do what you want to do.
4. After you're done, you deactivate your environment, just as in step 7 of installation.


## How to extend the program using maps
GMAP is built around the concept of maps. GMAP contains the physics, and provides the necessary tools. Maps, in turn, detail how to use these to obtain specific spectra. That means that GMAP cannot run without maps. When downloaded, GMAP comes with a few maps, but you might need a different one for your research. More maps can be found on [the GMAP_map_library github repository](https://https://github.com/lacourjansenlab/GMAP_map_library). **We strongly encourage people sharing their maps through there!**

Regardless of whether you downloaded a map from the mapping repository, a paper's SI, or somewhere else, these are the steps for loading it into GMAP:
1. Install GMAP.
2. Navigate, in a command line / terminal, to the location where you want to create a maps directory (where you will store all your maps).
3. Run the following command: ``GMAP Setup .`` This will create two directories: sourcefiles_copy, and maps_copy. Both will contain a copy of their respective directory within the GMAP installation files.
4. (optional) rename the maps_copy directory to something that suits you better.
5. Download your map of choice. Pay close attention on whether it is a 'Single' map, or a 'Pair' map, and remember the name of the map.
6. Depending on the type of map, place it into the 'Singles' or 'Pairs' directory within the maps_copy directory.
7. When preparing a calculation, add the following line in your input parameters file: ``maps_directory [path_to_maps_copy]``. Here, replace ``[path_to_maps_copy]`` with the path to that directory, including the directory maps_copy, but excluding the 'Singles' or 'Pairs' directories. **You want to refer to the whole library, not a specific map!** The path can either be relative, or absolute: ``maps_directory ../maps`` and ``maps_directory /home/yourname/GMAP_support_files/maps_copy`` can both work. Make sure to only have one line stating the maps_directory, though!
8. Carefully read the README of your newly installed map: does it need any extra steps? Does it put restrictions on the types of input (and kinds of calculations) it can produce well? Make sure to follow these things!
9. Now, you can choose your specific map using either the ``maps_to_use`` (Singles maps) or ``couplings_to_use`` (Pairs maps) parameters in your input file, and perform your calculation.


## how to compile C code

- compiled versions of the (VEG) c library are included in the respository. However, these are system dependent and you may need to recompile it for your own system.
- If you need to compile any files, be it for GMAP itself or for one of the maps used by it, make sure to navigate to the directory containing the .cpp file before following further compilation instructions.

### files that need compiling

* (always) GMAP/sourcefiles/VEG.cpp (see instructions below)
* (optional) GMAP/maps/Pairs/ProteinAmide_TCC/src/TCC_clib.cpp (modified command, see TCC map README). This is only needed if the map is used.
* (optional) GMAP/maps/Pairs/TrEsp/src/TrEsp_clib.cpp (modified command, see TrEsp map README). This is only needed if the map is used.

### windows

For GMAP to automatically recognize the compiled versions of scripts, the intended OS has to be added to the name. For windows (depending on your OS and python version), this means that the name should end in ```_Win32bit``` or ```_Win64bit```. If you do not do that, you can still manually supply your compiled file to GMAP, but the autodetection will not work.

- make sure to install microsoft visual studio (detailed instructions are a must - [AIM repository](github.com/kimvana/AIM) has them in the manual, page 12).
- through windows start menu, scroll trough list of programs, select visual studio folder, in there, the desired command prompt. x64 Native Tools for 64 bit windows, x86 Native Tools for 32 bit. __Make sure to open the command prompt in admin mode__.
- run one of the following commands: 
  ```cl.exe /LD /Fe: VEG_Win64bit scriptname.cpp``` (64 bit windows / python installation)
  ```cl.exe /LD /Fe: VEG_Win32bit scriptname.cpp``` (32 bit windows / python installation)
  (This step generates 4 files)
- The .dll file will be used by the program (you can either ignore or delete the other 3 generated ones).


### linux

For GMAP to automatically recognize the compiled versions of scripts, the intended OS has to be added to the name. For linux, this means that the name (including the extension) should end in ```_Linux.so```. If you do not do that, you can still manually supply your compiled file to GMAP, but the autodetection will not work.

- open terminal
- To compile the c-library use ```g++ -fPIC -shared -o scriptname_Linux.so scriptname.cpp```

For example, the VEG library can be compiled with ```g++ -fPIC -shared -o VEG_Linux.so VEG.cpp``` 

(if installed, using cc instead of g++ also works)


### mac

For GMAP to automatically recognize the compiled versions of scripts, the intended OS has to be added to the name. For mac, this means that the name (including the extension) should end in ```_MacOS.dylib```. If you do not do that, you can still manually supply your compiled file to GMAP, but the autodetection will not work.

Please note that depending on your mac version, the instructions are slightly different, and that Apple occasionally changes the way that the OS works resulting in changes in how to compile c++ code. Please, consult with updates from Apple if the commands below don't work on your system.

- open terminal
- Compile the code with one of the following commands (system dependent):
  - (Sonoma 14.6.1 and newer) ```cc -fPIC -dynamiclib -std=c++11 -stdlib=libc++ -o scriptname_MacOS.dylib scriptname.cpp```
  - (old MacOS) ```cc -fPIC -dynamiclib -o scriptname_MacOS.dylib scriptname.cpp```
  
For example, the VEG library can be compiled with ```g++ -fPIC -shared -o VEG_MacOS.dylib VEG.cpp``` or ```cc -fPIC -dynamiclib -std=c++11 -stdlib=libc++ -o VEG_MacOS.dylib VEG.cpp```



## Differences between GMAP and AIM

On a glance, the GMAP package might seem similar to AIM. How does it differ, and why should one want to switch from AIM to GMAP?

### GMAP has a larger scope
This might be pedantic, but GMAP is not comparable to AIM. AIM is a program that does a single thing, while GMAP is a package with multiple functionalities. One of the tools it contains, GEM, **is** comparable to AIM. It was the first tool to be developed within the package.


### Major differences between GMAP/GEM and AIM

- **Extended to UV-vis.** GEM is designed with a broader scope in mind from the beginning. One of the big consequences of this is that GEM can deal with electronic spectra predictions (UV-vis) much more easily than AIM could.
- **Non-orthorhomic system support.** The GMAP package has functionality that allows GEM to treat MD systems that have non-90-degree angles (not orthorhombic). These systems are often preferred in MD simulations (especilly of proteins), as they require less solvent.
- **Multiple-residue-oscillators.** GEM can work with singles/oscillators/dyes that live on multiple residues much more easily than AIM could. The Amide-I vibration of proteins (backbone) is one example of such an oscillator (and had a special implementation in AIM), other examples can be found in, for example, polymers.
- **Support for much larger MD systems.** GEM can output just energies/frequencies (the diagonal of the hamiltonian), while AIM had to output the full upper-diagonal hamiltonian. This means the largest feasible system (for subsequent treating with NISE) is at least tens of thousands of singles for GEM, opposed to roughly 1.5 thousand for AIM. 


### Differences in function between GMAP/GEM and AIM

- **Soft cutoff.** GMAP supports a soft cutoff where the 'weight' with which a charge is considered decreases with distance, whereas AIM either considered an atom, or it didn't.
- **Double positions output.** GMAP has the double-positions output, which NISE requires for some calculations.
- **NSA not yet implemented.** GMAP does not yet have the NSA algorithm implemented for faster electrostatics.
- **Mandatory C code.** GEM cannot run without a compiled C library. This makes the code much easier to maintain, and NISE also requires users to know how to compile C.
- **Coupling method selection.** GEM has more freedom than AIM with choosing coupling methods. GEM allows on a per-singles-map basis to choose the method, while AIM only allows turning dipole-dipole coupling on or off between (mis)matched pairs.
- **Missing features.** The following features were present in AIM, but not yet in GMAP/GEM. They are planned, so should be coming in due time. Need them now, contact us to see if we can find a workaround!
  - The functionality of the AIM parameter Scale_LR_coupling has not yet been implemented.
- **Easier whitelisting/blacklisting of singles** By default, GMAP can work with residue numbers and residue names (number/name of the residue of the zeroeth atom of the oscillator), but maps can add their own.
- **Legend file output.** The legend file contains a short description for each row in the hamiltonian/dipoles array. No more second-guessing which frequency belongs to which site!
- **Coupling method visualization output.** The couplingvis file has a diagram showing which coupling method has been used for which coupling value in the hamiltonian. Especially useful for mixed systems (e.g. proteins) that use multiple coupling methods at the same time.
- **Automated testing suite.** While most users won't see anything directly from the tests, their existence means its much easier to confirm the code functions as expected, with no bugs or the like.



### Quality of Life differences between GMAP/GEM and AIM

- **Code-free maps.** When creating a map for GMAP, it is no longer needed to know code. AIM however requires some python for every map. Often very simple code, but code nonetheless. GMAP can support a variety of maps without any code. Where code is needed (more complex mappings do), it is easier to integrate with the main program.
- **Automatic installation.** GMAP must be automatically installed, while this was optional for AIM. The GMAP installation is up-to-date with the newer conventions (whereas that of AIM isn't). This also means GMAP comes with a wheel. No more manual installation of dependencies.
- **Begone, resnames file.** The resnames file as it existed with AIM is no longer a thing. GMAP now has an influencer file system, but it is optional. During a run, the log file / command line output will mention which residues are(n't) considered, and only if that doesn't match the users needs/desires, will the user have to touch it. 
- **More legible command line output.** GMAP has a clearer output/report on the command line. It has colors (optional!), says what it's doing, and it reports more discovered information sooner (e.g. how many molecules were found in the MD system). It also indicates when (day/date/time) it started and thinks it'll finish. It still tells (as a stopwatch, in minutes/hours) how long it's been running, and how much longer it'll need, just like AIM.
- **Command line parameter specification.** GMAP allows parameter specification on the command line. Want to do a series of calculations with the same input file, but change one parameter per calculation? Prefer seeing parameter choices in the call to GMAP? This feature is the answer. You can still use input parameter files in the same way as you could with AIM.
- **Easier troubleshooting.** Got an error from the program? It now has an error code associated with it. There is an error page in the manual, listing all possible codes. Each code has some explanation and, where relevant, links to relevant documentation pages to get more information on how to solve the error.
- **More maps.** GMAP ships with a larger variety of maps than AIM did.
- **Incomplete maps.** GEM can deal with incomplete maps, as long as they specify their incompleteness correctly. No need to specify how to calculate the Raman tensor if you tell GEM your map cannot compute those anyways.
- **Calling GMAP from another python script.** While in theory possible, AIM never explicitly supported this. Now, GMAP contains no quit()'s, exit()'s, or sys.exit()'s. Only raise's. This makes it easier to catch a failed run when calling GMAP from another python script directly. There's also a function designed as the gateway into GMAP that your script can directly call.
- **Units are dead, long live the units.** GMAP is more flexible using different units than AIM was. The user can specify in which units the output files should be given, and custom-made maps can mention what units their contents assume.
- **Variable parameters.** This is highly-map specific, but the AmideBB and AmideSC maps are shipped with variable parameters. The angles/magnitudes used by various models can now be changed using those parameters.
- **Better file management.** A small change can make a huge difference. When GMAP creates new files, it makes sure to not overwrite any old ones of the same name if they already exist. Unless you tell it it should, of course!
- **Web-based manual.** The GMAP manual is [website-based](https://lacourjansenlab.github.io/GMAP/), instead of AIM's pdf documentation. Pages are linked together, and even the full documentation of the codebase can be found (helpful for developers).
- **Silencing warnings.** Ever screamed at your PC "I know, stupid thing! But it doesn't matter!"? We have. Now, you can tell the program to not complain/quit at any warning of your choice. However, use it at your own risk, the warnings are there for a reason!


## Version information

In order to use GMAP, you need to have a valid python installation. In this context, valid means that the correct version of python (and modules) is used, and that the python environment contains only modules whose versions work together.

Here follows an overview of versions that have been tested to work, but keep in mind that not every combination of every version and every module has been tested. The version printed in bold is the version used for development - this is considered the most stable. Versions between brackets have not all been tested, but are considered safe.

When you need to replicate a 'proven' environment - the `requirements_py3_10.txt` file is a mirror of the most used development environment in python 3.10.11. The `requirements_py3.13.txt` file is a mirror for a tested environment in python 3.13.1.

- Python: **3.10.11** (3.10.8 - 3.13.1)
- MDAnalysis: **2.9.0** (2.9.0 - 2.10.0)
- numba: **0.60.0** (0.60.0 - 0.62.1)
- numpy: **1.26.0** (1.26.0 - 2.3.5)
- build (dev build only): **1.3.0** (1.3.0)
- dataframe-image (dev build only): **0.2.7** (0.2.7)
- flake8 (dev build only): **7.3.0** (7.3.0)
- gprof2dot (dev build only): **2025.4.14** (2025.4.14)
- numpydoc (dev build only): **1.9.0** (1.9.0)
- pandas (dev build only): **2.3.2** (2.3.2 - 2.3.3)
- pydata-sphinx-theme (dev build only): **0.16.1** (0.16.1)
- pytest (dev build only): **8.4.2** (8.4.2 - 9.0.1)
- pytest-cov (dev build only): **7.0.0** (7.0.0)
- sphinx (dev build only): **8.1.3** (8.1.3 - 8.2.3)
- sphinx-design (dev build only): **0.6.1** (0.6.1)


