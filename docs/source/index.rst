Chaco Documentation
===================

Chaco is a Python toolkit for building interactive 2-D visualizations.  It
includes renderers for many popular plot types, built-in implementations of
common interactions with those plots, and a framework for extending and
customizing plots and interactions.  Chaco can also render graphics in a
non-interactive fashion to images, in either raster or vector formats, and it
has a subpackage for doing command-line plotting or simple scripting.

Chaco is built on three other Enthought packages:

  * `Traits <http://code.enthought.com/projects/traits>`_, as an event 
    notification framework
  * Kiva, for rendering 2-D graphics to a variety of backends across platforms
  * Enable, as a framework for writing interactive visual components, and for 
    abstracting away GUI-toolkit-specific details of mouse and keyboard
    handling

Currently, Chaco requires either wxPython or PyQt to display interactive plots,
but a cross-platform OpenGL backend (using Pyglet) is in the works, and it will
not require WX or Qt.

.. toctree::
  :maxdepth: 2

  quickstart.rst
  user_manual/tutorial.rst
  user_manual/index.rst
  programmers_reference.rst
  tech_notes.rst



* :ref:`search`
