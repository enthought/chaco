.. _installation:

*****************************
Installing and Building Chaco
*****************************

.. contents::

Overview
========

Chaco is one of the packages in the Enthought Tool Suite.  It can be installed
as part of ETS or as a separate package.  Even when it is installed as a 
standalone package, there are few other dependency packages that you will need.


Installing via EPD
===================

Chaco and the rest of ETS is installed as part of the `Enthought Python
Distribution (EPD) <http://www.enthought.com/epd>`_.  


easy_install
============

Chaco and its dependencies are available as binary eggs from the 
`Python Package Index <http://pypi.python.org/pypi>`_.


Linux Native Package
====================

On some supported distributions of Linux, native packages are available for
Chaco and the rest of ETS.

Debian
------

Ubuntu
------

Redhat
------


Building from Source
====================

Chaco itself is not very hard to build from source; there are only a few
C extensions and they build with most modern compilers.  Frequently the more
difficult to build piece is actually the Enable package on which Chaco 
depends.

Obtaining the source
--------------------

You can get Chaco and its dependencies from PyPI as source tarballs, or
you can download the source directly from Enthought's Subversion server.
The URL is::

    https://svn.enthought.com/svn/enthought/Chaco/trunk



