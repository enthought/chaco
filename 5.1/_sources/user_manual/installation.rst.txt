.. _installation:

============
Installation
============

There are several ways to get Chaco. The easiest way is through `Enthought
Deployment Manager <https://www.enthought.com/product/enthought-deployment-manager/>`_ (formerly EPD)
which provides environment management and package installation tools for
Windows, Linux and MacOS.  Chaco may also be available through a package manager
on your platform, such as apt on Ubuntu, yum on Redhat or
`MacPorts <http://www.macports.org/>`_ on OS X.  You can also build Chaco from
its `source code <https://github.com/enthought/chaco>`_, but because of the
dependencies, the easiest way by far is to install EDM.

.. _dependencies:

Dependencies
============

* `Python <https://www.python.org>`_ 2.7 or 3.5+

* `Traits <https://github.com/enthought/traits>`_, an event notification
  framework

* `TraitsUI <https://github.com/enthought/traits>`_, a rapid GUI application
  development framework

* `Kiva <https://github.com/enthought/enable>`_, part of the enable project,
  for rendering 2-D graphics to a variety of backends across platforms

* `Enable <https://github.com/enthought/enable/>`_, a framework for writing
  interactive visual components, and for abstracting away GUI-toolkit-specific
  details of mouse and keyboard handling.

* `NumPy <http://numpy.scipy.org/>`_, for dealing efficiently with large
  datasets

* Either `wxPython <http://www.wxpython.org/>`_, `PyQt
  <http://www.riverbankcomputing.co.uk/software/pyqt/intro>`_ (GPL or
  Commercial license) or `PySide <http://www.pyside.org/>`_ (LGPL license) to
  display interactive plots.

* (optionally) `ReportLab <https://bitbucket.org/rptlab/reportlab/src/default/>`_
  for PDF and PostScript output, and `Pillow <https://pillow.readthedocs.io/en/stable/>`_
  for raster image output.

Installing Chaco with EDM
=========================

To install via EDM, `download EDM
<https://www.enthought.com/product/enthought-deployment-manager/#download-edm>`_
for your platform and then do (from the command line)

.. code-block:: console

   edm install chaco pyqt5

to install Chaco, PyQt, and their dependencies and then

.. code-block:: console

   edm shell

to enter the Python environment with these packages installed.

PyQt5 is one of multiple supported backends. Other options include PyQt,
Pyside2, or wxPython.

Installing Chaco from Source
============================

If you choose to build Chaco rather than installing from a package manager
you will need a build environment that includes the standard C/C++ compiler
for your platform and Python version (see the Python documentation for more
information).  If you are going to build the dependencies you will also need
to install SWIG and you may want to install Cython if you want to update the
extension modules in Chaco.

Installation via Pip
--------------------

Chaco itself uses standard Python packaging via a setup.py script, so once
you have your build environment set up, you can install using Pip as you would
any other Python package.

.. code-block:: console

   $ pip install chaco

This will download the source distribution from PyPI and automatically build
Chaco and its dependencies for you.

.. note::
   If you have already installed Chaco and just want to update to the newest
   version, use

   .. code-block:: console

      $ pip install --upgrade chaco

Installation via setup.py
-------------------------

Alternatively, you can download the source code from the `Chaco GitHub
repository <https://github.com/enthought/chaco>`_ and use the standard
`setup.py` installation commands:

.. code-block:: console

   $ python setup.py install

This will attempt to install and build all dependencies as part of the
installation process.

Developer Live Installation
---------------------------

It is also possible to install a live-editable source installation
using

.. code-block:: console

   $ pip install -e .

at the top level of the Chaco source code.

Extension Modules
=================

Chaco contains a number of C extension modules used mainly for speed.  In the
current version of Chaco, the following extension modules are currently used:

``chaco/_cython_speedups.pyx``
    This is a Cython extension which speeds up a number of standard operations,
    currently mainly involving color maps.  If this is not available, Chaco will
    fall back on slower NumPy-based algorithms.

``chaco/contour/_cntr.c``
    Contour tracing on quadrilateral meshes.  This is required for contour plots.

``chaco/downsample/_lttb.pyx``
    Implementation of the "largest triangle three buckets" downsampling algorithm
    for line plots.  If this is not available, then "lttb" downsampling of line
    plots will fail.

The Chaco source code includes the generated ``*.c`` files for each of the Cython
``*.pyx`` files, so Cython is not required to build Chaco.  It is needed, however
if you are going to make changes to the Cython extension modules.

