=========================================
chaco: interactive 2-dimensional plotting
=========================================

http://www.github.com/enthought/chaco

http://docs.enthought.com/chaco

.. image:: https://api.travis-ci.org/enthought/chaco.png?branch=master
   :target: https://travis-ci.org/enthought/chaco
   :alt: Build status


Chaco is a Python plotting application toolkit that facilitates writing
plotting applications at all levels of complexity, from simple scripts with
hard-coded data to large plotting programs with complex data interrelationships
and a multitude of interactive tools. While Chaco generates attractive static
plots for publication and presentation, it also works well for interactive data
visualization and exploration.

Features
--------
- **Flexible drawing and layout**: Plots consist of graphical components which
  can be placed inside nestable containers for layout, positioning, and event
  dispatch. Every component has a configurable rendering loop with distinct
  layers and backbuffering. Containers can draw cooperatively so that layers
  span across the containment hierarchy.
- **Modular and extensible architecture**: Chaco is object-oriented from the
  ground up for ease of extension and customization. There are clear interfaces
  and abstract classes defining extension points for writing your own custom
  behaviors, from custom tools, plot types, layouts, etc. Most classes are
  also "subclass-friendly", so that subclasses can override one or two methods
  and everything else just works.
- **Data model for ease of extension and embedding**: Chaco separates the data
  from any transformations of the data that are needed for displaying it. This
  separation makes it easier to extend Chaco, or embed it in applications.

Prerequisites
-------------
Chaco is only supported on Python 2.7.x and Python >= 3.5.
You must have the following libraries installed before building or installing
Chaco:

* `Numpy <http://pypi.python.org/pypi/numpy>`_
* `setuptools <http://pypi.python.org/pypi/setuptools>`_
* `Cython <https://cython.org/>`_
* `enable <https://github.com/enthought/enable>`_

Mailing list
------------
To monitor discussions about Chaco, as well as the rest of the
`Enthought Tool Suite <http://code.enthought.com/>`_ (Traits, TraitsUI, Chaco,
Mayavi, ...), please refer to the `ets-users`
`google group <https://groups.google.com/forum/#!forum/ets-users>`_ .
