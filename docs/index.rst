.. esgf-build documentation master file, created by
   sphinx-quickstart on Fri Sep  1 11:08:10 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

esgf-build API documentation
======================================

esgf-build script is a Python module for building an ESGF distribution. The module contains several scripts that can be used to compile the source code of the various ESGF modules on Github (www.github.com/ESGF) into the distributable binary files.

ESGF Build process
There are several steps in building an ESGF distribution.
1. Fetching the code from Github
a. There is a function to purge the local repos and fetch fresh copies from Github
b. Another function can update all local repos listed in the configuration repo list to be in sync with the remote repos.  The user can choose either the devel or master branch to sync.


.. toctree::
   :maxdepth: 2
   :caption: API:

   api

   build



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
