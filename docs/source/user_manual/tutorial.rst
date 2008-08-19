
.. _tutorials:

Overview of Tutorials
=====================

Chaco is a plotting application toolkit for Python.  It can be used
to create stand-alone plots, but it is designed for interactive plotting.
There are three basic ways to use Chaco:

    #. Using Traits UI to create a stand-alone application or a widget
       that can be integrated with an existing Traits UI view.  See
       :ref:`tutorial_traits`.

    #. Creating a stand-alone wxPython application, or embedding a Chaco
       plot within a wxPython application.  See :ref:`tutorial_wx`.

    #. Using the Chaco Shell command-line plotting interface to build
       plots, in a Matlab or gnuplot-like style.  See 
       :ref:`tutorial_ipython`.

There is a separate tutorial covering each of these uses.  For those who are
relatively new to developing GUI applications, we recommend approach #1.  Using
Chaco with Traits UI allows the scientist or novice programmer to easily
develop plotting applications, but it also provides them room to grow as their
requirements change and increase in complexity.

For those who are familiar with GUI programming using WX or Qt, the second
tutorial shows how to embed Chaco components directly into an enclosing widget,
panel, or dialog.  It also demonstrates more advanced usages like using
a wxPython Timer to display live, updating data streams.

.. toctree::
    :maxdepth: 2

    tutorial_traits.rst
    tutorial_wx.rst
    tutorial_ipython.rst

