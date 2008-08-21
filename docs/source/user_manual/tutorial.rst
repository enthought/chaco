
.. _tutorials:

Tutorials
=========

There are three tutorials for Chaco, each corresponding to one of the
three different ways to use Chaco:

    #. Using Traits UI to create a stand-alone application or a widget
       that can be integrated with an existing Traits UI view.  See
       :ref:`tutorial_traits`.
        
       This is the by far the most common usage of Chaco.  It is a good
       approach for those who are relatively new to developing GUI
       applications.  Using Chaco with Traits UI allows the scientist or novice
       programmer to easily develop plotting applications, but it also provides
       them room to grow as their requirements change and increase in
       complexity.

       Traits UI can also be used by a more experienced developer to build more
       involved applications, and Chaco can be used to embed visualizations or
       to leverage interactive graphs as controllers for an application.

    #. Creating a stand-alone wxPython or Qt application, or embedding a Chaco
       plot within an existing application.  See :ref:`tutorial_wx`.

       This tutorial is suited for those who are familiar with programming
       using wxPython or Qt and prefer to write directly to those toolkits.   It
       shows how to embed Chaco components directly into an enclosing widget,
       panel, or dialog.  It also demonstrates more advanced usages like using
       a wxPython Timer to display live, updating data
       streams.

    #. Using the Chaco Shell command-line plotting interface to build plots, in
       a Matlab or gnuplot-like style.  Although this approach doesn't lend itself
       to building more reusable utilities or applications, it can be a quick way
       to get plots on the screen and build one-off visualizations.  See
       :ref:`tutorial_ipython`.

All three tutorials introduce a newcomer to the core concepts of Chaco and
some of their content overlaps.  By the end of any of the above tutorials,
the reader will have seen how to:

    * create a Python script or module that creates a Chaco plot

    * display scatter, line, and image plots on the screen

    * save a plot to disk

    * plot multiple data items in overlapping, side-by-side, or other
      layouts

    * create a custom plot renderer

    * create a custom tool that interacts with the mouse
       
The reader will also be familiar with the concepts of data sources, components,
containers, renderers, the graphics context, tools, and events.  Armed with
this knowledge, the reader can move on to the :ref:`Modules and Classes
<modules_and_classes>` and the :ref:`programmers_reference` sections.

.. toctree::
    :maxdepth: 2

    tutorial_traits.rst
    tutorial_wx.rst
    tutorial_ipython.rst

