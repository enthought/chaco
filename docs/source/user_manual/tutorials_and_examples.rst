
.. _tutorials:

Tutorials and examples
======================

.. toctree::
  :maxdepth: 1

  tutorial_1.rst
  tutorial_van_der_waal.rst
  tutorial_hyetograph.rst
  tutorial_wx.rst
  tutorial_ipython.rst
  
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

    #. Tutorial 2, :ref:`tutorial_van_der_waal`, is another example of creating a data
       model and then using Traits and Chaco to rapidly create interactive 
       plot GUIs.
       
    #. :ref:`tutorial_hyetograph` introduces the ``on_trait_listener`` 
       decorator and uses Chaco, simple Traits views, and live GUI interaction.

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

