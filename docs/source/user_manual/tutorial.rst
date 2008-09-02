
.. _tutorials:

Tutorials
=========

.. note::

    (8/28/08) This section is currently being updated to unify the information
    from several past presentations and tutorials.
    Until it is complete, here are links to some of those.  The HTML versions
    are built using `S5 <http://meyerweb.com/eric/tools/s5/>`_, which uses
    Javascript heavily.  You can navigate the slide deck by using left and right
    arrows, as well as a drop-down box in the lower right-hand corner.

        * `SciPy 2006 Tutorial <http://code.enthought.com/projects/files/chaco_scipy06/chaco_talk.html>`_ (Also available in `pdf <http://code.enthought.com/projects/files/Data_Exploration_with_Chaco.pdf>`_)

        * `Pycon 2007 presentation slides <http://code.enthought.com/projects/files/chaco_pycon07/index.html>`_

        * `SciPy 2008 Tutorial slides (pdf) <https://svn.enthought.com/svn/enthought/Chaco/trunk/docs/scipy08_tutorial.pdf>`_: These slides are currently being converted into the :ref:`tutorial_1` tutorial.


There are several tutorials for Chaco, each covering slightly different
aspects:

    #. Tutorial 1, :ref:`tutorial_1`, introduces some basic concepts of 
       how to use Chaco and Traits UI to do basic plots, customize
       layout, and add interactivity.  
       
       Although Traits UI is not required to use Chaco, it is the by far the
       most common usage of Chaco.  It is a good approach for those who are
       relatively new to developing GUI applications.  Using Chaco with Traits
       UI allows the scientist or novice programmer to easily develop plotting
       applications, but it also provides them room to grow as their
       requirements change and increase in complexity.

       Traits UI can also be used by a more experienced developer to build more
       involved applications, and Chaco can be used to embed visualizations or
       to leverage interactive graphs as controllers for an application.

    #. :ref:`tutorial_wx`: Creating a stand-alone wxPython application, or
       embedding a Chaco plot within an existing Wx application.

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

.. [COMMENT]::
    #. Tutorial 2., :ref:`tutorial_2`, goes into more detail about plot
       customization and 

.. [COMMENT]::
    The reader will also be familiar with the concepts of data sources, components,
    containers, renderers, the graphics context, tools, and events.  Armed with
    this knowledge, the reader can move on to the :ref:`Modules and Classes
    <modules_and_classes>` and the :ref:`programmers_reference` sections.

