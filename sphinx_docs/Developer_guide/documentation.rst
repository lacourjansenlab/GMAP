################
Documentation
################

GMAP now comes not only with the source files for building documentation, but also with them built and uploaded to github pages. The intent is for this process to be as automatic as possible, so when any changes are made to the pipeline, it should be done such that no extra work is added to development work on the program itself.


*********************************
Version numbers
*********************************

There is a version of the documentation for each minor version. GMAP uses the convention of v[major].[minor].[patch], with an optional extra prerelease label at the end. So, v3.1.4-alpha2 is the second alpha of patch 4 of version 3.1.

The documentation is built at the occurence of two different triggers:
- something is pushed to the development branch
- a new release is created through the github releases UI.

.. important::
    When a new release is created through the GitHub releases UI, the tag should reflect the full version identifier, including the 'v' (always), and the '-something' when applicable. Including the dash. Don't use the dash if it is not a prerelease.


When to use what version
========================

The major version should increase when something major happens, possibly worthy of a new publication. Perhaps a new program, just like GEM.

The minor version should increase when a functional change/addition is made. New keywords, new options, you name it.

The patch version is intended for bug fixes and similarly small updates. It *might* also be a good idea to use it to pull important changes to key maps from the GMAP_map_library repository.

The prerelease label should be used only when a formal github release is desired/required, but the program is not yet ready to be formally updated to a new version. Prereleases (and the development branch) will never be marked as stable in the docs, everything else will.



Branches and versions
=====================

When an issue is to be tackled, a separate branch is created for it. This process is described in detail in :ref:`the devguide workflow<DevGuide_page_home_workflow>`.
On the development branch, many things can be tested. Of course, things should already be tested on the issue branches, with development being a final collecting place. Impatient users could try new features there, at their own risk.
When the senior developers think it is time for a new release, the development branch should not merge any new pull requests. Instead, the team should test the current branch, fix any bugs, and polish the codebase, documentation, and other files. When this is done, a pull request to main can be opened, and after thorough review, merged to main. After that merger, development can receive new pull requests again.

Why mention this here? Well, what happens with the old code on main? What if a bug is found on an old version? In that case, the following procedure should be considered.
- The version of the program for which the bug is reported will be denoted vx.y.z here.
- Starting at vx.y.z, work up to newer versions of the program. Look for the first version that does not just add functionality, but changes the flow of the program. What version actively behaves differently (ignoring bugs)? Lets call that version va.b.c.
- The user cannot always be expected to upgrade to va.b.c (or even newer) as this might have unexpected effects on research. Ideally, the last version *before* va.b.c will be taken and updated with a bug fix. However, developers cannot be expected to fix bugs on too many different releases, so a choice has to be made. For example, the team could decide to only support a version for a certain amount of time, or to choose a maximum amount of versions to support.
- When a version is chosen to receive a bug fix, compare its version number to the latest stable version. If it is an older version, a branch should be created (if it doesn't exist already) from the release that should receive the bug fix (so, for example, from release v1.3.6), and **not** from main. The new branch should be named 'maintenance/1.3.x' in this example case. In your case, make the major and minor version match those of the release you're branching from. It should be the newest patch of that minor version.
- if not done already, create a new issue for the bug, along with a working branch. Base that branch on the relevant maintenance branch. Fix the issue following the normal workflow (except you don't need to stay up to date with the development branch).
- After proper testing, open a pull request from the issue branch to the relevant maintenance branch. From there, create a release, with a new patch number.
- If multiple versions need the same bug fix, you can open a pull request from the bugfix branch to the other relevant maintenance (and development/main if applicable) branches, and create new releases. See warning below!

.. warning::
    Be very careful with pulling a bugfix to other branches, as the fix might need to be different there. The safest option is to create a new bugfix branch from scratch for each version, the easiest (and somewhat safe, mileage may vary) way is to only have one bugfix branch for the oldest version to receive the fix.

Following the above, there should at most be one maintenance branch per minor version, never more.


.. warning::
    Do not manually change anything on the github pages branch, unless you really know what you're doing, and have explicitly discussed this with the senior developers. This branch is intended to only be accessed by the github workflows, and hosts the github pages website.



**************************
Versions and documentation
**************************

The structure of the documentation reflects the above. The documentation is able to show legacy versions, but will only show the most recent patch of each minor version. Alongside that, there is also a development version of the docs.

The address 'stable' also exists, but it is a symlink to the most recent stable version.

If a prerelease is created, the documentation for it will be built. It will be added to the version dropdown file, too, but it will not be marked as stable. It will not show up in the dropdown menu of any version. Still, a direct link (containing the new minor version) will work and can be shared along with the prerelease.




***************
Jinja templates
***************

There are a few jinja templates available for apidoc to use. This is what they do:


module.rst.jinja
================

This one is used to generate the apidoc pages for python files (e.g. parameter_parser.rst).


Package.rst.jinja
=================

This one is used to generate the apidoc pages for directories (e.g. GMAP, GMAP.src.tools).



