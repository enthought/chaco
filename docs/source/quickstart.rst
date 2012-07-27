##########
Quickstart
##########

+----------------------------------------+--------------------------------------+
|.. image::  images/simple_line.png      |.. image::  images/scalar_function.png|
|   :height: 300 px                      |   :height: 300 px                    |
|   :align: center                       |   :align: center                     |
+----------------------------------------+--------------------------------------+

This section is meant to help users on well-supported platforms and common
Python environments get started using Chaco as quickly as possible. As part of
the `Enthought Tool Suite <http://code.enthought.com/>`_, Chaco users can
subscribe to the `enthought-dev
<https://mail.enthought.com/mailman/listinfo/enthought-dev>`_  mailing list to
post questions, consult archives and share tips.

Licensing
=========

As part of the `Enthought Tool Suite <http://code.enthought.com/>`_, Chaco is
free and open source under the BSD licence.

Installation Overview
=====================

.. _dependencies:

Dependencies
------------
Chaco requires Python version 2.5 or later to be installed. Chaco is built on
three other Enthought packages:

  * `Traits <https://github.com/enthought/traits>`_, as an event notification
    framework,
  * `Kiva <https://github.com/enthought/enable>`_, part of the enable project,
    for rendering 2-D graphics to a variety of backends across platforms,
  * `Enable <https://github.com/enthought/enable/>`_, as a framework for
    writing interactive visual components and for abstracting away
    GUI-toolkit-specific details of mouse and keyboard handling.

It also relies on two external packages:
  * `Numpy <http://numpy.scipy.org/>`_, to deal efficiently with large
    datasets.
  * Either `wxPython <http://www.wxpython.org/>`_ or  `PyQt
    <http://www.riverbankcomputing.co.uk/software/pyqt/intro>`_ to display
    interactive plots. As an alternative to PyQt, Chaco is being more and more
    tested using the `PySide <http://www.pyside.org/>`_ toolkit (LGPL license).

  .. .. note
  .. ::
  .. In addition to wxPython or PyQt a cross-platform OpenGL backend (using
  .. Pyglet) is in the works, and it will not require WX or Qt.

Installation
------------

There are several different ways to get Chaco. You can either download and
install the `Enthought Python Distribution (EPD)
<http://www.enthought.com/epd>`_ or build Chaco on your machine. Because of the
number of packages required to build Chaco and its dependencies **we highly
recommend to install EPD**.


  1. Install the Enthought Python Distribution.  Chaco, the rest of the
     Enthought Tool Suite and a lot more are bundled in it.  This allows for
     the installation of Chaco and all its dependencies to be installed at
     once. **These packages will be linked to a new instance of python**.

     Go to the `EDP download page
     <http://www.enthought.com/products/getepd.php>`_ and get the appropriate
     version for your platform (Windows, Mac, Linux, Solaris are available).
     After running the installer, you will have a working version of Chaco and
     several examples.

     The EPD Free distribution is **free for all users** and contains all that
     you need to use Chaco.


Building Chaco on your machine requires to build Chaco and each of its
dependencies. It has the advantage of installing it on top of the python
instance of your OS.  But the building process might be challenging and will
require SWIG, Cython and several development libraries to be installed. 


  2. *(Linux only)* Install via the distribution's packaging mechanism.
     Enthought provide .debs installers for Debian and Ubuntu and .rpm
     installers for Redhat. 


  3. Download sources as a project from the `Chaco github repository
     <https://github.com/enthought/chaco>`_ or alternatively as a part of the
     ETS (for details see http://code.enthought.com/source/). Please refer to
     the :ref:`installation` section for more detailed instructions.

  4. Install Chaco and its :ref:`dependencies` from `PyPI
     <http://pypi.python.org/pypi>`_ using `easy_install
     <http://packages.python.org/distribute/easy_install.html>`_ (part of
     setuptools) or using `pip <http://www.pip-installer.org/en/latest/>`_. For
     example using easy_install, simply type ::

        easy_install Chaco

Chaco built-in Examples
=======================

To test installation and find examples of what can be done with Chaco, Chaco is
shipped with example files. Almost all of the Chaco examples are stand-alone
files that can be run individually, from any location. Depending on how you
installed Chaco, you may or may not have the examples already.


Location
--------

1. If you installed Chaco as part of EPD, the location of the examples depends
   on your platform:

   * On Windows, they are in the Examples\\ subdirectory of your installation
     location.  This is typically
     :file:`C:\\Python27\\Examples\\Chaco-<version>`.  On MS Windows these
     examples can be browsed from the start menu, by clicking
     :command:`Applications > Enthought > Examples`.

   * On Linux, they are in the :file:`Examples/Chaco-<version>` subdirectory of
     your installation location.

   * On Mac OS X, they are in the
     :file:`/Applications/Enthought/Examples/Chaco-<version>` directory.


2. If you downloaded and installed Chaco from source (from Github or via the
   PyPI tar.gz file), the examples are located in the :file:`examples/`
   subdirectory inside the root of the Chaco source tree, next to :file:`docs/`
   and the :file:`enthought/` directories.


3. If you happen to be on a machine with Chaco installed, but you don't know
   the exact installation mechanism, then you might need to download the
   examples separately using Git (or Subversion for older versions of Chaco):

   * For the most up-to-date version of the examples:

     :command:`git clone https://github.com/enthought/chaco/tree/master/examples`

   * For the most up-to-date version of the examples using the old version of
     the namespace (importing chaco using ``from enthought.chaco``):
  
     :command:`git clone https://github.com/enthought/chaco/tree/old-namespace/examples`

   * ETS 3.0 or Chaco 3.0:
  
     :command:`svn co https://svn.enthought.com/svn/enthought/Chaco/tags/3.0.0/examples`

   * ETS 2.8 or Chaco 2.0.x:
  
     :command:`svn co https://svn.enthought.com/svn/enthought/Chaco/tags/enthought.chaco2_2.0.5/examples`

Chaco examples can be found in the :file:`examples/demo/` and
:file:`examples/tutorials/` directories. Some examples are classified by themes
and located in separate directories.  Almost all of the Chaco examples are
stand-alone files that can be run individually. They can be executed from
command line and we will illustrate this first.  We will then show how to run
Chaco in an interactive way from IPython. This "shell" mode is more familiar to
Matplotlib or Matlab users.

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

* To pan the plot, hold down the left mouse button inside the plot area (but
  not on the legend) and drag the mouse.

* To zoom the plot:

    * Mouse wheel: scroll up to zoom in, and scroll down to zoom out.
    
    * Zoom box: Press "z", and then draw a box region to zoom in on. (There is
      no box-based zoom out.) Press Ctrl-Left and Ctrl-Right to go back and
      forward in your zoom box history.
    
    * Drag: hold down the right mouse button and drag the mouse up or down. Up
      zooms in, and down zooms out.
    
    * For any of the above, press Escape to resets the zoom to the original
      view.

* To move the legend, hold down the right mouse button inside the legend and
  drag it around. Note that you can move the legend outside of the plot area.

* To exit the plot, click the "close window" button on the window frame
  (Windows, Linux) or choose the Quit option on the Python menu (on Mac).
  Alternatively, can you press Ctrl-C in the terminal.

You can run most of the examples in the top-level :file:`examples` directory,
the :file:`examples/demo/basic/` directory, and the
:file:`examples/demo/shell/` directory.  The :file:`examples/demo/advanced/`
directory has some examples that require additional data or packages. In
particular,

* :file:`spectrum.py` requires that you have PyAudio installed and a working
  microphone.  

* :file:`data_cube.py` needs to download about 7.3mb of data from the Internet
  the first time it is executed, so you must have a working Internet
  connection. Once the data is downloaded, you can save it so you can run the
  example offline in the future.

For detailed information about each built-in example, see the :ref:`examples`
section.



First plots from IPython
------------------------

While all of the Chaco examples can be launched from the command line using the
standard Python interpreter, if you have IPython installed, you can poke around
them in a more interactive fashion.

Chaco provides a subpackage, currently named the "Chaco Shell", for doing
command-line plotting like Matlab or Matplotlib.  The examples in the
:file:`examples/demo/shell/` directory use this subpackage, and they are
particularly amenable to exploration with IPython.

The first example we'll look at is the :file:`lines.py` example.  First, we'll
run it using the standard Python interpreter:

    :command:`python lines.py`

This shows two overlapping line plots.

.. image:: images/lines.png

You can interact with the plot in the following ways:

    * To pan the plot, hold down the left mouse button inside the plot area and
      dragging the mouse.

    * To zoom the plot:

        * Mouse wheel: scroll up zooms in, and scroll down zooms out.

        * Zoom box: hold down the right mouse button, and then draw a box
          region to zoom in on.  (There is no box-based zoom out.)  Press
          Ctrl-Left and Ctrl-Right to go back and forward in your zoom box
          history.
        
        * For either of the above, press Escape to reset the zoom to the
          original view.

Now exit the plot, and start IPython with the ``--gui=wx`` option [#guiqt]_: ::

    ipython --gui=wx

This tells IPython to start a wxPython mainloop in a background thread.  Now
run the previous example again::

    In [1]: run lines.py

This displays the plot window, but gives you another IPython prompt.  You can
now use various commands from the :mod:`chaco.shell` package to interact with
the plot.  

* Import the shell commands::

    In [2]: from chaco.shell import *

* Set the X-axis title::

    In [3]: xtitle("X data")

* Toggle the legend::

    In [4]: legend()

After running these commands, your plot looks like this:

.. image:: images/lines_final.png

The :func:`chaco_commands` function display a list of commands with brief
descriptions.

You can explore the Chaco object hierarchy, as well. The :mod:`chaco.shell`
commands are just convenience functions that wrap a rich object hierarchy that
comprise the actual plot. See the :ref:`tutorial_ipython` section for
information on all you can do with Chaco from within IPython.


Chaco Plot integrated in a Traits application
=============================================
Let's create from scratch the simplest possible Chaco plot embedded inside a
`Traits <http://github.enthought.com/traits/>`_ application.

First, some imports will bring in the necessary components::

  from chaco.api import ArrayPlotData, Plot
  from enable.component_editor import ComponentEditor

  from traits.api import HasTraits, Instance
  from traitsui.api import View, Item

The imports from `chaco` and `enable` will support the creation of the plot.
The imports from `traits` bring in the components to embed the plot inside a
trait application. (Refer to the `traits documentation
<http://github.enthought.com/traits/>`_ for more details about building an
interactive application using Traits.) Now let's create a trait class with a
view that contains only 1 element: a Chaco plot inside a slightly customized
window::

  class MyPlot(HasTraits):
      plot = Instance(Plot)
      traits_view = View(Item('plot', editor = ComponentEditor(), show_label = False),
                         width = 500, height = 500,
                         resizable = True, title = "My line plot")

A few options have been set to control the window containing the plot.  Now, at
creation, we would like to pass our data. Let's assume that they are in the
form of a set of points with coordinates contains in 2 numpy arrays x and y.
Then, the Plot object must be created::

  def __init__(self, x, y, *args, **kw):
      super(MyPlot, self).__init__(*args, **kw)
      plotdata = ArrayPlotData(x=x,y=y)
      plot = Plot(plotdata)
      plot.plot(("x","y"), type = "line", color = "blue")
      plot.title = "sin(x)*x**3"
      self.plot = plot

Deriving from HasTraits the new class can use all the power of Traits and the
call to super() in its constructor makes sure this object possesses the
attributes and methods of its parent class.  Now let's use our trait object:
simply generate some data, pass it to an instance of MyPlot and call
configure_traits to create the UI::

  import numpy as np
  x = np.linspace(-14,14,100)
  y = np.sin(x)*x**3
  lineplot = MyPlot(x,y)
  lineplot.configure_traits()

The result should look like

.. image:: images/mylineplot.png

This might look like a lot of code to visualize a function. But this represents
a relatively simple basis to build full featured applications with a custom UI
and custom tools on top of the plotting functionality such as those illustrated
in the examples. For example, the trait object allows you to create controls
for your plot at a very high level, add these controls to the UI with very
little work, add listeners to update the plot when the data changes. Exploring
the capabilities of Chaco allows you to create tools to interact with the plot,
and overlays for example allow you to make these tools intuitive to use and
visually appealing.


.. rubric:: Footnotes

.. [#guiqt] Starting from IPython 0.12, it is possible to use the Qt backend
    with ``--gui=qt``. Make sure that the environment variable ``QT_API``
    is set correctly, as described `here
    <http://ipython.org/ipython-doc/dev/interactive/reference.html?highlight=qt_api#pyqt-and-pyside>`_
