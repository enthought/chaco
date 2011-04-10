##########
Quickstart
##########

This section is meant to help users on well-supported platforms and common
Python environments get started using Chaco as quickly as possible.  If your
platform is not listed here, or your Python installation has some quirks, then
some of the following instructions might not work for you.  If you encounter
any problems in the steps below, please refer to the :ref:`installation`
section for more detailed instructions.

Installation Overview
=====================

There are several different ways to get Chaco:

* Install the Enthought Python Distribution.
  Chaco and the rest of the Enthought Tool Suite are bundled with it.  Go to
  the main `Enthought Python Distribution (EPD)
  <http://www.enthought.com/epd>`_ web site and download the appropriate
  version for your platform.  After running the installer, you will have a
  working version of Chaco.

  .. note::
     Enthought Python Distribution is free for academic users.

* *(Windows, Mac)* Install from PyPI using easy_install (part of setuptools)
  from the command line:

  :command:`easy_install Chaco`

* *(Linux)* Install distribution-specific eggs from Enthought's repository.
  See the `ETS wiki <https://svn.enthought.com/enthought/wiki/Install#UsingEnthoughtsEggRepo>`_
  for instructions for installing pre-built binary eggs for your specific
  distribution of Linux.

* *(Linux)* Install via the distribution's packaging mechanism.  We provide
  .debs for Debian and Ubuntu and .rpms for Redhat.  (TODO)

* Download source as tarballs or from Subversion and build.  See 
  the :ref:`installation` section.

Chaco requires Python version 2.5.



Running Some Examples
=====================

Depending on how you installed Chaco, you may or may not have the examples already.

If you installed Chaco as part of EPD, the location of the examples depends on 
your platform:

* On Windows, they are in the :file:`Examples\\` subdirectory of your installation
  location.  This is typically :file:`C:\\Python25\\Examples`.

* On Linux, they are in the :file:`Examples/` subdirectory of your installation
  location.

* On Mac OS X, they are in the :file:`/Applications/<EPD Version>/Examples/`
  directory.

If you downloaded and installed Chaco from source (via the PyPI tar.gz file, or
from an SVN checkout), the examples are located in the :file:`examples/` subdirectory
inside the root of the Chaco source tree, next to :file:`docs/` and the :file:`enthought/`
directories.

If you installed Chaco as a binary egg from PyPI for your platform, or if you
happen to be on a machine with Chaco installed, but you don't know the exact
installation mechanism, then you will need to download the examples separately
using Subversion:

* ETS 3.0 or Chaco 3.0:
  
  :command:`svn co https://svn.enthought.com/svn/enthought/Chaco/tags/3.0.0/examples`

* ETS 2.8 or Chaco 2.0.x:
  
  :command:`svn co https://svn.enthought.com/svn/enthought/Chaco/tags/enthought.chaco2_2.0.5/examples`

.. [COMMENT]::
    (TODO):  Add links to examples tarball.

Almost all of the Chaco examples are stand-alone files that can be run
individually, from any location.

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
http://code.enthought.com/projects/files/ETS3_API/enthought.chaco.html

The API docs for Chaco2 (in ETS 2.7.1) are at:
http://code.enthought.com/projects/files/ets_api/enthought.chaco2.html


