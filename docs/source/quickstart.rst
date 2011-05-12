##########
Quickstart
##########

This section is meant to help users on well-supported platforms and common
Python environments get started using Chaco as quickly as possible. As part of the 
`Enthought Tool Suite <http://code.enthought.com/>`_, Chaco users can subscribe 
to the `enthought-dev <https://mail.enthought.com/mailman/listinfo/enthought-dev>`_  
**mailing list** to post questions, consult archives and share tips.

Licencing
=========

As part of the `Enthought Tool Suite <http://code.enthought.com/>`_, Chaco is free 
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
  * `Numpy <http://numpy.scipy.org/>`_, to deal efficiently with large datasets,
  * Either `wxPython <http://www.wxpython.org/>`_ or `PyQt <http://www.riverbankcomputing.co.uk/software/pyqt/intro>`_ to display interactive plots.

  .. note 
  .. ::
  .. In addition to wxPython or PyQt a cross-platform OpenGL backend (using Pyglet) is in the works, and it will not require WX or Qt.

Installation
------------

There are several different ways to get Chaco. You can either download and install the 
`Enthought Python Distribution (EPD) <http://www.enthought.com/epd>`_ or build Chaco 
on your machine. Because of the number of packages required to build Chaco and its 
dependencies **we highly recommend to install EPD**. If you encounter
any problems in the steps below, please refer to the :ref:`installation`
section for more detailed instructions or to the 
`enthought-dev <https://mail.enthought.com/mailman/listinfo/enthought-dev>`_  
**mailing list** to post questions, consult archives and share tips.


  1. Install the Enthought Python Distribution.
     Chaco, the rest of the Enthought Tool Suite and a lot more are bundled in it. 
     This allows for the installation of Chaco and all its dependencies to be 
     installed at once. **These packages will be linked to a new instance of python**.
     Go to the main `EPD <http://www.enthought.com/epd>`_ 
     web site and download the appropriate version for your platform (Windows, MAC, Linux, 
     Solaris are available).  After running the installer, you will have a working version of Chaco and 
     several examples.

  .. note::
     Enthought Python Distribution is free for academic users.

Building Chaco on your machine requires to build Chaco and each of its dependencies. It 
has the advantage of installing it on top of the python instance of your OS.
But the building process might be challenging and will require SWIG, Cython and several 
development libraries to be installed. 


  2. *(Linux only)* Install via the distribution's packaging mechanism.  Enthought provide .debs 
  installers for Debian and Ubuntu and .rpm installers for Redhat. 


  3. Download sources as a project from the 
  `Chaco github repository <https://github.com/enthought/chaco>`_ or alternatively as a part 
  of the ETS (for details see http://code.enthought.com/source/). Please refer to the 
  :ref:`installation` section for more detailed instructions.

  4. Install Chaco and its :ref:`dependencies` from `PyPI <http://pypi.python.org/pypi>`_ using 
  `easy_install <http://packages.python.org/distribute/easy_install.html>`_ (part of setuptools) 
  or using `pip <http://www.pip-installer.org/en/latest/>`_. For example using easy_install, 
  simply type

  :command:`easy_install Chaco`


Running Some Examples
=====================

To test installation and find examples of what can be done with Chaco, Chaco is shipped with 
example files. Almost all of the Chaco examples are stand-alone files that can be run 
individually, from any location. Depending on how you installed Chaco, you may or may not 
have the examples already.

If you installed Chaco as part of EPD, the location of the examples depends on 
your platform:

* On Windows, they are in the :file:`Examples\\` subdirectory of your installation
  location.  This is typically :file:`C:\\Python25\\Examples`.

* On Linux, they are in the :file:`Examples/` subdirectory of your installation
  location.

* On Mac OS X, they are in the :file:`/Applications/<EPD Version>/Examples/`
  directory.

If you downloaded and installed Chaco from source from the 
`Chaco github repository <https://github.com/enthought/chaco>`_, the examples are located in the 
:file:`examples/` subdirectory inside the root of the Chaco source tree, next to 
:file:`docs/` and the :file:`enthought/` directories.


All of the following instructions that involve the command line assume that 
you are in the same directory as the examples.

Command line
------------

Run the ``simple_line`` example:

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
directory, the :file:`examples/basic/` directory, and the :file:`examples/shell/`
directory.  The :file:`examples/advanced/` directory has some examples that
may or may not work on your system:

* :file:`spectrum.py` requires that you have PyAudio installed and a working
  microphone.  

* :file:`data_cube.py` needs to download about 7.3mb of data from the Internet
  the first time it is executed, so you must have a working
  Internet connection. Once the data is downloaded, you can save it so you 
  can run the example offline in the future.

For detailed information about each built-in example, see the :ref:`examples`
section.

IPython
-------

While all of the Chaco examples can be launched from the command line using the
standard Python interpreter, if you have IPython installed, you can poke around
them in a more interactive fashion.

Chaco provides a subpackage, currently named the "Chaco Shell", for doing
command-line plotting like Matlab or Matplotlib.  The examples in the
:file:`examples/shell/` directory use this subpackage, and they are particularly
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
commands are just convenience functions that wrap a rich object hierarchy
that comprise the actual plot. See the :ref:`tutorial_ipython` section
for information on more complex and interesting things you can do with Chaco
from within IPython.


Start Menu (MS Windows)
-----------------------

If you installed the Enthought Python Distribution (EPD), you have
shortcuts installed in your Start Menu for many of the Chaco examples.  You can
run them by just clicking the shortcut.  (This just invokes python.exe on the
example file itself.)


Creating a Plot
===============

(TODO)


Further Reading
===============

Once you have Chaco installed, you can either visit the :ref:`tutorials`
to learn how to use the package, or you can run the examples (see the
:ref:`examples` section).


Presentations
-------------

There have been several presentations on Chaco at previous PyCon and 
SciPy conferences.  Slides and demos from these are described below.

Currently, the examples and the scipy 2006 tutorial are the best ways  
to get going quickly. (See http://code.enthought.com/projects/files/chaco_scipy06/chaco_talk.html)

Some tutorial examples were recently added into the examples/tutorials/scipy2008/  
directory on the trunk.  These examples are numbered and introduce  
concepts one at a time, going from a simple line plot to building a  
custom overlay with its own trait editor and reusing an existing tool  
from the built-in set of tools.  You can browse them on our SVN server  
at:
https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/tutorials/scipy2008

.. _api_docs:

API Docs
--------

The API docs for Chaco 3.0 (in ETS 3.0) are at:
http://code.enthought.com/projects/files/ETS3_API/chaco.html

The API docs for Chaco2 (in ETS 2.7.1) are at:
http://code.enthought.com/projects/files/ets_api/chaco2.html
