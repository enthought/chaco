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
Distribution (EPD) <http://www.enthought.com/epd>`_.  If you have installed
EPD, then you already have Chaco!


easy_install
============

Chaco and its dependencies are available as binary eggs for Windows and Mac OS
X from the `Python Package Index <http://pypi.python.org/pypi>`_.  For these
platforms, you can do a single command to install Chaco and its prerequisites::

    $ easy_install Chaco

Because eggs do not distinguish between various distributions of Linux,
Enthought hosts its own egg repository for Linux eggs.  See the `ETS wiki
<https://svn.enthought.com/enthought/wiki/Install#UsingEnthoughtsEggRepo>`_ for
instructions for installing pre-built binary eggs for your specific
distribution of Linux.

Linux Native Package
====================

On some supported distributions of Linux, packages are available in the native
package format (e.g. RPM, DEB) for Chaco and the rest of ETS.

Debian
------

(TODO)

Ubuntu
------

(TODO)

Redhat
------

(TODO)

Building from Source
====================

Chaco itself is not very hard to build from source; there are only a few
C extensions and they build with most modern compilers.  Frequently the more
difficult to build piece is actually the Enable package on which Chaco 
depends.

.. [COMMENT]::

    Obtaining the source
    --------------------

    You can get Chaco and its dependencies from PyPI as source tarballs, or
    you can download the source directly from Enthought's Subversion server.
    The URL is::

        https://svn.enthought.com/svn/enthought/Chaco/trunk

.. note:: 
   This section is current under construction.  Please see the `ETS Install
   From Source <https://svn.enthought.com/enthought/wiki/Build>`_ wiki page
   for more information on building Chaco and the rest of ETS on your platform.

