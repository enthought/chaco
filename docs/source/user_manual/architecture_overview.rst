*********************
Architecture Overview
*********************

.. note::

   At this time, this is an overview of not just Chaco, but also Kiva and
   Enable.

Core Ideas
==========

The Chaco toolkit is defined by a few core architectural ideas:

* **Plots are compositions of visual components**

  Everything you see in a plot is some sort of graphical widget,
  with position, shape, and appearance attributes, and with an
  opportunity to respond to events.

* **Separation between data and screen space**

  Although everything in a plot eventually ends up rendering into a common
  visual area, there are aspects of the plot which are intrinsically
  screen-space, and some which are fundamentally data-space.  Preserving
  the distinction between these two domains allows us to think about
  visualizations in a structured way.

* **Modular design and extensible classes**

  Chaco is meant to be used for writing tools and applications, and code
  reuse and good class design are important. We use the math behind the
  data and visualizations to give us architectural direction and conceptual
  modularity. The Traits framework allows us to use events to couple
  disjoint components at another level of modularity.

  Also, rather than building super-flexible core objects with myriad
  configuration attributes, Chaco's classes are written with subclassing in
  mind.  While they are certainly configurable, the classes themselves are
  written in a modular way so that subclasses can easily customize
  particular aspects of a visual component's appearance or a tool's
  behavior.


The Relationship Between Chaco, Enable, and Kiva
================================================

Chaco, Enable, and Kiva are three packages in the Enthought Tool Suite.
They have been there for a long time now, since almost the beginning of
Enthought as a company.  Enthought has delivered many applications using
these toolkits. The Kiva and Enable packages are bundled together in the
"Enable" project.

Kiva
----

Kiva is a 2-D vector drawing library for Python.  It serves a purpose
similar to `Cairo <http://cairographics.org/>`_.  It allows us to compose
vector graphics for display on the screen or for saving to a variety of
vector and image file formats.  To use Kiva, a program instantiates a Kiva
GraphicsContext object of an appropriate type, and then makes drawing calls
on it like gc.draw_image(), gc.line_to(), and gc.show_text().  Kiva
integrates with windowing toolkits like wxWindows and Qt, and it has an
OpenGL backend as well.  For wxPython and Qt, Kiva actually performs a
high-quality, fast software rasterization using the Anti-Grain Geometry
(AGG) library.  For OpenGL, Kiva has a python extension that makes native
OpenGL calls from C++.

Kiva provides a GraphicsContext for drawing onto the screen or saving out to
disk, but it provides no mechanism for user input and control. For this
"control" layer, it would be convenient to have to write only one set of event
callbacks or handlers for all the platforms we support, and all the toolkits on
each platform. Enable provides this layer. It insulates all the rendering and
event handling code in Chaco from the minutiae of each GUI toolkit.
Additionally, and to some extent more importantly, Enable defines the concept of
"components" and "containers" that form the foundation of Chaco's architecture.
In the Enable model, the top-most Window object is responsible for dispatching
events and drawing a single component. Usually, this component is a container
with other containers and components inside it. The container can perform layout
on its internal components, and it controls how events are subsequently
dispatched to its set of components.

Enable
------

Almost every graphical component in Chaco is an instance of an
Enable component or container.  We're currently trying to push more of the
layout system (implemented as the various different kinds of Chaco plot
containers) down into Enable, but as things currently stand, you have to
use Chaco containers if you want to get layout.  The general trend has been
that we implement some nifty new thing in Chaco, and then realize that it
is a more general tool or overlay that will be useful for other
non-plotting visual applications.  We then move it into Enable, and if
there are plotting-specific aspects of it, we will create an appropriate
subclass in Chaco to encapsulate that behavior.

The sorts of applications that can and should be done at the Enable level
include things like a visual programming canvas or a vector drawing tool.
There is nothing at the Enable level that understands the concept of
mapping between a data space to screen space and vice versa.  Although
there has been some debate about the incorporating rudimentary mapping into
Enable, for the time being, if you want some kind of canvas-like thing to
model more than just pixel space on the screen, implement it using
the mechanisms in Chaco.

.. [COMMENT]: A diagram would be helpful to illustrate the following paragraph.

The way that Enable hooks up to the underlying GUI toolkit system is via an
:class:`enable.Window` object. Each toolkit has its own implementation of this
object, and they all subclass from :class:`enable.AbstractWindow`. They usually
contain an instance of the GUI toolkit's specific window object, whether it's a
:class:`wx.Window` or :class:`Qt.QWidget` or :class:`pyglet.window.Window`. This
instance is created upon initialization of the enable.Window and stored as the
:attr:`control` attribute on the Enable window. From the perspective of the GUI
toolkit, an opaque widget gets created and stuck inside a parent control (or
dialog or frame or window). This instance serves as a proxy between the GUI
toolkit and the world of Enable. When the user clicks inside the widget area,
the :attr:`control` widget calls a method on the enable.Window object, which
then in turn can dispatch the event down the stack of Enable containers and
components. When the system tells the widget to draw itself (e.g., as the result
of a PAINT or EXPOSE event from the OS), the enable.Window is responsible for
creating an appropriate Kiva GraphicsContext (GC), then passing it down through
the object hierarchy so that everyone gets a chance to draw. After all the
components have drawn onto the GC, for the AGG-based bitmap backends, the
enable.Window object is responsible for blitting the rastered off-screen buffer
of the GC into the actual widget's space on the screen. (For Kiva's OpenGL
backend, there is no final blit, since calls to the GC render in immediate mode
in the window's active OpenGL context, but the idea is the same, and the
enable.Window object does perform initialization on the GL GraphicsContext.)

Some of the advantages to using Enable are that it makes mouse and key
events from disparate windowing systems all share the same kind of
signature, and be accessible via the same name.  So, if you write bare
wxPython and handle a key_pressed event in wx, this might generate a value
of wx.WXK_BACK.  Using Enable, you would just get a "key" back and its
value would be the string "Backspace", and this would hold true on Qt4 and
Pyglet.  Almost all of the event handling and rendering code in Chaco is
identical under all of the backends; there are very few backend-specific
changes that need to be handled at the Chaco level.

The enable.Window object has a reference to a single top-level graphical
component (which includes containers, since they are subclasses of
component).  Whenever it gets user input events, it recursively dispatches
all the way down the potentially-nested stack of components.  Whenever a
components wants to signal that it needs to be redrawn, it calls
self.request_redraw(), which ultimately reaches the enable.Window, which
can then make sure it schedules a PAINT event with the OS.  The nice thing
about having the enable.Window object between the GUI toolkits and our
apps, and sitting at the very top of event dispatch, is that we can easily
interject new kinds of events; this is precisely what we did to enable all
of our tools to work with Multitouch.

The basic things to remember about Enable are that: 

* Any place that your GUI toolkit allows you stick a generic widget, you
  can stick an Enable component (and this extends to Chaco components, as
  well).  Dave Morrill had a neat demonstration of this by embedding
  small Chaco plots as cells in a wx Table control.  

* If you have some new GUI toolkit, and you want to provide an Enable
  backend for it, all you have to do is implement a new Window class for
  that backend.  You also need to make sure that Kiva can actually
  create a GraphicsContext for that toolkit.  Once the kiva_gl branch is
  committed to the trunk, Kiva will be able to render into any GL
  context. So if your newfangled unsupported GUI toolkit has a
  GLWindow type of thing, then you will be able to use Kiva, Enable, and
  Chaco inside it.  This is a pretty major improvement to
  interoperability, if only because users now don't have to download and
  install wxPython just to play with Chaco.


Chaco
-----

At the highest level, Chaco consists of:

    * Visual components that render to screen or an output device
      (e.g., :class:`LinePlot`, :class:`ScatterPlot`, :class:`PlotGrid`, 
      :class:`PlotAxis`, :class:`Legend`)

    * Data handling classes that wrap input data, interface with
      application-specific data sources, and transform coordinates
      between data and screen space (e.g., :class:`ArrayDataSource`,
      :class:`GridDataSource`, :class:`LinearMapper`)

    * Tools that handle keyboard or mouse events and modify other
      components (e.g., :class:`PanTool`, :class:`ZoomTool`, 
      :class:`ScatterInspector`)


