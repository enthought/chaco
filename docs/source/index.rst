Chaco Documentation
===================

Chaco is a Python package for building interactive and custom 2-D plots and
visualizations. It has been optimized for displaying efficiently large 
datasets. 
It includes renderers for many popular plot types, built-in implementations of
common interactions with those plots, and a framework for extending and
customizing plots and interactions.  Chaco can also render graphics in a
non-interactive fashion to images, in either raster or vector formats, and it
has a subpackage for doing command-line plotting or simple scripting.

.. image:: images/scalar_function.png

Chaco is built on three other Enthought packages:

  * `Traits <http://code.enthought.com/projects/traits>`_, as an event 
    notification framework
  * `Kiva <https://svn.enthought.com/enthought/wiki/Kiva>`_, for rendering 2-D graphics to a variety of backends across platforms
  * `Enable <http://code.enthought.com/projects/enable/>`_, as a framework for writing interactive visual components, and for 
    abstracting away GUI-toolkit-specific details of mouse and keyboard
    handling

To deal efficiently with large datasets, it also requires on `Numpy 
<http://numpy.scipy.org/>`_ to be installed.
Finally, Chaco currently requires either wxPython or PyQt to display 
interactive plots, but a cross-platform OpenGL backend (using Pyglet) is in 
the works, and it will not require WX or Qt.

.. toctree::
  :maxdepth: 2

  quickstart.rst
  user_manual/tutorial.rst
  user_manual/index.rst
  programmers_reference.rst
  tech_notes.rst



* :ref:`search`
