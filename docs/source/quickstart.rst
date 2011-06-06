
.. last updated on Jun 5th 2011 by Jonathan Rocher


##########
Quickstart
##########
+----------------------------------------+--------------------------------------+
|.. image:: _images/simple_line.png      |.. image:: _images/scalar_function.png|
|   :width: 400 px                       |   :width: 400 px                     |
|   :align: center                       |   :align: center                     |
+----------------------------------------+--------------------------------------+

This section is meant to help users on well-supported platforms and common
Python environments get started using Chaco as quickly as possible.  If your
platform is not listed here, or your Python installation has some quirks, then
some of the following instructions might not work for you.  If you encounter
any problems in the steps below, please refer to the :ref:`installation`
section for more detailed instructions.

Licencing
=========

Chaco as part of the `Enthought Tool Suite <http://code.enthought.com/>`_ is free 
and open source under the BSD licence.

Installation Overview
=====================

.. _dependencies:

Dependencies
------------
Chaco requires Python version 2.5 or later to be installed. Chaco is built on three other 
Enthought packages:

  * `Traits <http://code.enthought.com/projects/traits>`_, as an event notification framework,
  * `Kiva <https://svn.enthought.com/enthought/wiki/Kiva>`_, for rendering 2-D graphics to a variety of backends across platforms,
  * `Enable <http://code.enthought.com/projects/enable/>`_, as a framework for writing interactive visual components, and for abstracting away GUI-toolkit-specific details of mouse and keyboard handling.

It also relies on two external packages:
  * `Numpy <http://numpy.scipy.org/>`_, to deal efficiently with large datasets.
  * Either `wxPython <http://www.wxpython.org/>`_ or  `PyQt <http://www.riverbankcomputing.co.uk/software/pyqt/intro>`_ to display interactive plots. As an alternative to PyQt, Chaco is being more and more tested using the `PySide <http://www.pyside.org/>`_ toolkit (LGPL license).

  .. .. note
  .. ::
  .. In addition to wxPython or PyQt a cross-platform OpenGL backend (using Pyglet) is in the works, and it will not require WX or Qt.

Installation
------------

There are several different ways to get Chaco. You can either download and install the 
`Enthought Python Distribution (EPD) <http://www.enthought.com/epd>`_ or build Chaco 
on your machine. Because of the number of packages required to build Chaco and its 
dependencies we highly recommend to install EPD.

* Install the Enthought Python Distribution.
  Chaco, the rest of the Enthought Tool Suite and a lot more are bundled in it. 
  This allows for the installation of Chaco and all its dependencies to be 
  installed at once. These packages will be linked to a new instance of python.
  Go to the main `EPD <http://www.enthought.com/epd>`_ 
  web site and download the appropriate version for your platform (Windows, MAC, Linux, 
  Solaris).  After running the installer, you will have a working version of Chaco and 
  several examples.

  .. note::
     Enthought Python Distribution is free for academic users and a free version of EPD
     containing Chaco will be released soon.

* *(Linux)* Install via the distribution's packaging mechanism.  Enthought provide .debs 
installers for Debian and Ubuntu and .rpm installers for Redhat.

Building Chaco on your machine requires to build Chaco and each of its dependencies. 
This might be challenging and will require SWIG and Cython to be installed.

* Download sources as a project from the `Chaco github repository <https://github.com/enthought/chaco>`_ or alternatively as a part of the ETS (for details see http://code.enthought.com/source/). Please refer to the :ref:`installation` section for more detailed instructions.

* Install Chaco and its :ref:`dependencies` from `PyPI <http://pypi.python.org/pypi>`_ using 
  `easy_install <http://packages.python.org/distribute/easy_install.html>`_ (part of setuptools) 
  or using `pip <http://www.pip-installer.org/en/latest/>`_. For example using easy_install, 
  simply type

  :command:`easy_install Chaco`
  

Chaco Gallery
=============
Examples of what can be done with Chaco is available in our `Chaco gallery <http://code.enthought.com/projects/chaco/gallery.php>`_.

Running Some Examples
=====================

Location
--------

Depending on how you installed Chaco, you may or may not have the examples already.

1. If you installed Chaco as part of EPD, the location of the examples depends on 
   your platform:

   * On Windows, they are in the Examples\\ subdirectory of your installation
     location.  This is typically :file:`C:\\Python27\\Examples\\Chaco-<version>`. 
     On MS Windows these examples can be browsed from the start menu, by clicking 
     :command:`Applications > Enthought > Examples`.

   * On Linux, they are in the :file:`Examples/Chaco-<version>` subdirectory of your installation
     location.

   * On Mac OS X, they are in the :file:`/Applications/Enthought/Examples/Chaco-<version>`
     directory.


2. If you downloaded and installed Chaco from source (from Github or via the PyPI tar.gz file), 
   the examples are located in the :file:`examples/` subdirectory
   inside the root of the Chaco source tree, next to :file:`docs/` and the :file:`enthought/`
   directories.


3. If you happen to be on a machine with Chaco installed, but you don't know the exact
   installation mechanism, then you might need to download the examples separately
   using Git (or Subversion for older versions of Chaco):

   * For the most up-to-date version of the examples:

     :command:`git clone https://github.com/enthought/chaco/tree/master/examples`

   * For the most up-to-date version of the examples using the old version of the namespace 
     (importing chaco using <i>from enthought.chaco</i>):
  
     :command:`git clone https://github.com/enthought/chaco/tree/old-namespace/examples`

   * ETS 3.0 or Chaco 3.0:
  
     :command:`svn co https://svn.enthought.com/svn/enthought/Chaco/tags/3.0.0/examples`

   * ETS 2.8 or Chaco 2.0.x:
  
     :command:`svn co https://svn.enthought.com/svn/enthought/Chaco/tags/enthought.chaco2_2.0.5/examples`

Chaco examples can be found in the :file:`examples/demo/` and :file:`examples/tutorials/` 
directories. Some examples are classified by themes and located in separate directories. 
Almost all of the Chaco examples are stand-alone files that can be run individually. They 
can be from command line and we will illustrate this first as Chaco's main goal is to 
provide a package for building integrated applications. We will then show how to run Chaco 
in an interactive way from IPython. This "shell" mode is more common to Matplotlib or 
Matlab users.

.. note::
   Some of these examples can be visualized in our 
   `Chaco gallery <http://code.enthought.com/projects/chaco/gallery.php>`_.


First plots from command line
-----------------------------

From the examples directory, run the ``simple_line`` example:

  :command:`python simple_line.py`

This opens a plot of several Bessel functions and a legend.

  .. image:: images/simple_line.png

You can interact with the plot in several ways:

* To pan the plot, hold down the left mouse button inside the plot area
  (but not on the legend) and drag the mouse.

* To zoom the plot:

    * Mouse wheel: scroll up to zoom in, and scroll down to zoom out.
    
    * Zoom box: Press "z", and then draw a box region to zoom in on. (There
      is no box-based zoom out.) Press Ctrl-Left and Ctrl-Right to go
      back and forward in your zoom box history.
    
    * Drag: hold down the right mouse button and drag the mouse up
      or down. Up zooms in, and down zooms out.
    
    * For any of the above, press Escape to resets the zoom to the
      original view.

* To move the legend, hold down the right mouse button inside the
  legend and drag it around. Note that you can move the legend
  outside of the plot area.

* To exit the plot, click the "close window" button on the window frame
  (Windows, Linux) or choose the Quit option on the Python menu (on
  Mac).  Alternatively, can you press Ctrl-C in the terminal.

You can run most of the examples in the top-level :file:`examples`
directory, the :file:`examples/demo/basic/` directory, and the :file:`examples/demo/shell/`
directory.  The :file:`examples/demo/advanced/` directory has some examples that
require additional data or packages. In particular, 

* :file:`spectrum.py` requires that you have PyAudio installed and a working
  microphone.  

* :file:`data_cube.py` needs to download about 7.3mb of data from the Internet
  the first time it is executed, so you must have a working
  Internet connection. Once the data is downloaded, you can save it so you 
  can run the example offline in the future.

For detailed information about each built-in example, see the :ref:`examples`
section.



First plots from IPython
------------------------

While all of the Chaco examples can be launched from the command line using the
standard Python interpreter, if you have IPython installed, you can poke around
them in a more interactive fashion.

Chaco provides a subpackage, currently named the "Chaco Shell", for doing
command-line plotting like Matlab or Matplotlib.  The examples in the
:file:`examples/demo/shell/` directory use this subpackage, and they are particularly
amenable to exploration with IPython.

The first example we'll look at is the :file:`lines.py` example.  First, we'll
run it using the standard Python interpreter:

    :command:`python lines.py`

This shows two overlapping line plots.

.. image:: images/lines.png

You can interact with the plot in the following ways:

    * To pan the plot, hold down the left mouse button inside the plot area
      and dragging the mouse.

    * To zoom the plot:

        * Mouse wheel: scroll up zooms in, and scroll down zooms out.

        * Zoom box: hold down the right mouse button, and then draw a box region
          to zoom in on.  (There is no box-based zoom out.)  Press Ctrl-Left and
          Ctrl-Right to go back and forward in your zoom box history.
        
        * For either of the above, press Escape to reset the zoom to the
          original view.

Now exit the plot, and start IPython with the -wthread option:

    :command:`ipython -wthread`

This tells IPython to start a wxPython mainloop in a background thread.  Now
run the previous example again::

    In [1]: run lines.py

This displays the plot window, but gives you another
IPython prompt.  You can now use various commands from the :mod:`chaco.shell`
package to interact with the plot.  

* Import the shell commands::

    In [2]: from enthought.chaco.shell import *

* Set the X-axis title::

    In [3]: xtitle("X data")

* Toggle the legend::

    In [4]: legend()

After running these commands, your plot looks like this:

.. image:: images/lines_final.png

The :func:`chaco_commands` function display a list of commands with brief
descriptions.

You can explore the Chaco object hierarchy, as well. The :mod:`chaco.shell` 
commands are just convenience functions that wrap a rich object hierarchy
that comprise the actual plot. See the :ref:`tutorial_ipython` section
for information on all you can do with Chaco from within IPython.


Chaco Plot integrated in a Traits application
=============================================
Let's create from scratch the simplest possible Chaco plot embedded inside 
a `Traits <http://github.enthought.com/traits/>`_ application.

First, some imports will bring in the necessary components::

  from enthought.chaco.api import ArrayPlotData, Plot
  from enthought.enable.component_editor import ComponentEditor

  from enthought.traits.api import HasTraits, Instance
  from enthought.traits.ui.api import View, Item

The imports from chaco and enable will support the creation of the plot. The 
imports from traits bring in the components to embed the plot inside a trait 
application. (Refer to the `traits documentation <http://github.enthought.com/traits/>`_ 
for more details about building an interactive application using Traits.)
Now let's create a trait class with a view that contains only 1 element: a Chaco 
plot::

  class MyPlot(HasTraits):
      plot = Instance(Plot)
      traits_view = View(Item('plot', editor = ComponentEditor()),
                         width = 500, height = 500,
                         resizable = True, title = "My line plot")

A few options have been set to control the window containing the plot.
Now, at creation, we would like to pass our data. Let's assume that 
they are in the form of a set of points with coordinates contains in 2 
numpy arrays x and y. Then, the Plot object must be created::

  def __init__(self, x, y, *args, **kw):
      super(MyPlot, self).__init__(*args, **kw)
      plotdata = ArrayPlotData(x=x,y=y)
      plot = Plot(plotdata)
      plot.plot(("x","y"), type = "line", color = "blue")
      plot.title = "sin(x)*x**3"
      self.plot = plot

Deriving from HasTraits the new class can use all the power
of Traits and the call to super() in its constructor makes sure this
object possesses the attributes and methods of its parent class.
Now let's use our trait object: simply generate some data, pass 
it to an instance of MyPlot and call configure_traits to create the UI::

  import numpy as np
  x = np.linspace(-14,14,100)
  y = np.sin(x)*x**3
  lineplot = MyPlot(x,y)
  lineplot.configure_traits()

The result should look like

.. image:: images/mylineplot.png

This might look like a lot of code to visualize a function. But this 
represents a relatively simple basis to build full featured applications 
with a custom UI and custom tools on top of the plotting functionality 
such as those illustrated in the examples. For example, the trait object 
allows you to create controls for your plot at a very high level, add 
these controls to the UI with very little work, add listeners to update 
the plot when the data changes. Exploring the capabilities of Chaco can 
allows you to create tools to interact with the plot, and overlays for 
example allow you to make these tools intuitive to use and visually 
appealling.

.. _going_further:

Further Reading and ressources
==============================

You can also learn more about Chaco:

* following some tutorials that come with the Chaco package,

* Exploring our `Chaco gallery <http://code.enthought.com/projects/chaco/gallery.php>`_ with examples,

* following demos of Chaco given during webinars Enthought to EPD subscribers,

* reading seminar slides posted on conference websites, 

* reading about the API from the developer guide.


Tutorials
---------

For more details on how to use Chaco to embed powerful plotting 
functionality inside applications, refer to the :ref:`tutorials`. 
In particular some tutorial examples were recently added into the 
:file:`examples/tutorials/scipy2008/` directory.  These examples are 
numbered and introduce  
concepts one at a time, going from a simple line plot to building a  
custom overlay with its own trait editor and reusing an existing tool  
from the built-in set of tools.  You can browse them on our SVN server  
at:
https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/tutorials/scipy2008
Finally, it is recommended to explore the examples 
(:ref:`examples` section) as they are regularly updated to reflect the most recent 
changes and recommended ways to use Chaco. 


.. _chaco_webinars:

Enthought webinars
------------------
The video webinars given in  as part of the Enthought webinar 
series cover building interactive plotting using Chaco. If you are an 
EPD user, you can find the video, the slides, and the demo code for 
each webinar covering Chaco. 

The first one (April 2010) demoes how to use Chaco as your plotting 
tool (https://www.enthought.com/repo/epd/webinars/2010-04InteractiveChaco/ ). 

The seconds (October 2010) illustrates how to building interactive 2D visualization (see 
https://www.enthought.com/repo/epd/webinars/2010-10Building2DInteractiveVisualizations/ ).


.. _chaco_presentations:


Presentations
-------------

There have been several presentations on Chaco at previous PyCon and 
SciPy conferences.  Slides and demos from these are described below.

Currently, the examples and the scipy 2006 tutorial are the best ways
to get going quickly (see 
http://code.enthought.com/projects/files/chaco_scipy06/chaco_talk.html ).
Chaco was also presented at PyCon 2007 and Scipy 2011 and the slides 
are available from http://code.enthought.com/projects/files/chaco_pycon07/


.. _api_docs:

Developers references and API Docs
-----------------------------------

For developers, more details about the architecture, and the API can be found in 
the :ref:`programmers_reference`. The API for older versions of Chaco can be found at 
http://code.enthought.com/projects/files/ETS3_API/enthought.chaco.html for Chaco 3.0 
(in ETS 3.0) and at http://code.enthought.com/projects/files/ets_api/enthought.chaco2.html 
for Chaco2 (in ETS 2.7.1).

