Chaco |version|
===============

Chaco is a Python package for building interactive and custom 2-D plots and
visualizations.  Chaco facilitates writing plotting applications at all levels
of complexity, from simple scripts with hard-coded data to large plotting
programs with complex data interrelationships and a multitude of interactive
tools.  While Chaco generates attractive static plots for publication and
presentation, Chaco differs from tools like Matplotlib in that it also works
well for dynamic interactive data visualization and exploration.  Chaco is part
of the Enthought Tool Suite.

.. image::  images/chaco_show.png
   :width: 800 px
   :align: center

Chaco includes renderers for many popular plot types, built-in implementations of
common interactions with those plots, and a framework for extending and
customizing plots and interactions.  Chaco can also render graphics in a
non-interactive fashion to images, in either raster or vector formats, and it
has a subpackage for doing command-line plotting or simple scripting.

Installation
------------

Chaco and all of its dependencies (including the PyQt backend) can be
installed using the `Enthought Deployment Manager
<https://www.enthought.com/product/enthought-deployment-manager/>`_ (formerly
EPD):

.. code-block:: console

   edm install chaco pyqt5

For full installation options, including installation from source, see the
:ref:`installation instructions <installation>`.

Documentation
-------------

For developers exploring Chaco for the first time, these tutorials and examples
give a good overview of the capabilities of Chaco:

* :ref:`Sample Plot Gallery <examples>`
* :ref:`Tutorial: Interactive plotting with Chaco <tutorial>`
* Examples:

  - :ref:`Modeling Van del Waal's Equations <tutorial_van_der_waal>`
  - :ref:`Creating an interactive Hyetograph <tutorial_hyetograph>`

There is also a :ref:`FAQ <faq>` which provides answers to issues and common
tricks that help when building Chaco applications.

For comprehensive documentation, we have:

* :ref:`User Guide <user_guide>`
* :ref:`Developer Reference <developer_reference>`
* :ref:`API Reference <api_reference>`
* :ref:`search`

Reporting bugs and contributing
-------------------------------

Since Chaco is open source and hosted on
`Github <https://github.com/enthought/chaco>`_, the development version can
always be checked out from Github, forked, and modified at will. When a bug is
found, please submit an issue in the
`issue page <https://github.com/enthought/chaco/issues>`_. If you would like to
share a bug fix or a new feature, simply submit a Pull Request from your fork.
Don't forget to specify very clearly what code to run to reproduce the issue,
what the logic of the fix is and to add one or more unit tests to ensure future
stability. The Pull Request description can and often needs to contain
screenshots of the issue or the fix.

License
-------

As part of the `Enthought Tool Suite <http://docs.enthought.com/ets>`_, Chaco is
free and open source under a BSD license:

.. include:: ../../LICENSE.txt
