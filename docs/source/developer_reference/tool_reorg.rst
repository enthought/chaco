.. _tool_reorg:

###########
Tools Reorg
###########

This is the current starte of Pan and Zoom tools accross Chaco and Enable
(red = in enable):

.. graphviz::

    digraph OldToolInheritanceTree {
        BetterZoom -> DragZoom;
        BetterZoom -> BetterSelectingZoom;
        ZoomTool [
            label=<ZoomTool<BR /><FONT POINT-SIZE="14">Currently just an alias for BetterSelectingZoom</FONT>>
        ];
        BetterSelectingZoom -> ZoomTool [dir=none];
        RectZoom [
            label=<RectZoom<BR /><FONT POINT-SIZE="14">Just sets 2 traits on ZoomTool</FONT>>
        ];
        ZoomTool -> RectZoom;
        TrackingZoom [
            label=<RectZoom<BR /><FONT POINT-SIZE="14">Defines one additional method on ZoomTool</FONT>>
        ];
        ZoomTool -> TrackingZoom;
        DragTool [fillcolor=red, style=filled];
        DragTool -> DragZoom;
        BaseZoomTool [fillcolor=red, style=filled];
        ViewportZoomTool [fillcolor=red, style=filled];
        ViewportPanTool [fillcolor=red, style=filled];
        DragTool -> ViewportPanTool;
        BaseZoomTool -> ViewportZoomTool;
        PanTool;
        TrackingPanTool [
            label=<TrackingPanTool<BR /><FONT POINT-SIZE="14">Defines one additional method on PanTool</FONT>>
        ];
        PanTool -> TrackingPanTool;
        PanTool2 [
            label=<PanTool2<BR /><FONT POINT-SIZE="14">Not in chaco.tools.api, very rarely used.<BR />However, seems to have been intended as improvement over PanTool.</FONT>>
        ];
        DragTool -> PanTool2;
    }

Until recently, there had also been a ``BaseZoomTool`` and ``SimpleZoom``
living in chaco. These now exist in enable (with some trimming / modifications)
and are the ``BaseZoomTool`` and ``ViewportZoomTool`` above.  Additionally,
we recently removed the duplicate of the enable ``DragTool`` which was living
in chaco.

``RectZoom`` and ``TrackingZoom`` are intended as convenience classes but end
up clouding the api.  Instead we should simply have a ``ZoomTool`` class (which
is actually ``BetterSelectingZoom``, but that code can be copied over and
``BetterSelectingZoom`` removed).  This is the "default" / go-to zoom tool most
users will use. If they want the current ``RectZoom`` or ``TrackingZoom``
functionality, there should simply be an easy way to configure a ``ZoomTool``
to do so.  Either by setting a trait like ``rect=True`` or ``tracking=True``,
or perhaps with some class method on ``ZoomTool``.  This way it will be more
obvious what tool you want if you want zoom functionality
(you want the ``ZoomTool``!) and it can be confiugred to your needs.
Similar logic applies to ``TrackingPanTool`` and either of the ``PanTool``s.
Although currently, ``TrackingPanTool`` subclasses ``PanTool1``.

The current ``BetterZoom`` class can be renamed as ``BaseZoomTool``. The way things
currently are (with ``ZoomTool`` an alias for ``BetterSelectingZoom``), the "default"
zoom tool has selecting functionality. There are situations like ``DragZoom``
where you don't want this.  AFAICT, users are not expected to use ``BetterZoom``
directly. As such, it makes sense to make it an explicit base class.

In enable, I do not really see why ``BaseZoomTool`` needs to be its own class.
It is only used by ``ViewportZoomTool``, and is not exposed in any api module.
Further, from what I can tell, enable zoom functionality is only possible via
a ``Canvas`` with a ``Viewport``.  So only having a ``ViewportZoomTool`` seems
reasonable.  However, if the class is anticipated to be used as a base class
for other zoom tool variants, ``BaseZoomTool`` can easily stay.

Additionally, either ``pan_tool.PanTool`` or ``pan_tool2.Pantool`` should be
removed. (I still need to investigate the feature disparity / advantages of one
over the other, if any exist)

After some initial investigation it is clear much of the code is copy pasted.
However, some obvious differences include:

* PanTool1 subclasses ``BaseTool`` whereas PanTool2 subclasses ``DragTool``
* PanTool1 has ``pan_{right/left/up/down}_key`` traits, PanTool2 does not
* PanTool1 also allows "middle" for ``drag_button``, PanTool2 (inheriting
  ``drag_button`` from enable ``DragTool``) only allows "left" or "right"
* PanTool1 sets event state to "panning" and defines "panning" specific methods
  whereas PanTool2 overrides methods on DragTool (e.g. ``dragging``,
  ``drag_cancel``, ``drag_end``)

Potentially relevant issues include enthought/chaco#519, and enthought/enable#90.

The following is a proposal for a new class heirarchy:

.. graphviz::

    digraph NewToolInheritanceTree {
        BaseZoomTool [
            label=<BaseZoomTool<BR /><FONT POINT-SIZE="14">Formally BetterZoom</FONT>>
        ];
        ZoomTool [
            label=<ZoomTool<BR /><FONT POINT-SIZE="14">Formally BetttterSelectingZoom / ZoomTool</FONT>>
        ]
        BaseZoomTool -> ZoomTool;
        BaseZoomTool -> DragZoom;
        DragTool [fillcolor=red, style=filled];
        DragTool -> DragZoom;
        ViewportZoomTool [fillcolor=red, style=filled];
        ViewportPanTool [fillcolor=red, style=filled];
        DragTool -> ViewportPanTool;
        PanTool [style="dotted"];
        PanTool2 [
            label=<PanTool2<BR /><FONT POINT-SIZE="14">Not in chaco.tools.api, very rarely used.<BR />However, seems to have been intended as improvement over PanTool.</FONT>>,
            style="dotted"
        ];
        DragTool -> PanTool2;
    }



Migration Steps:

#. Rename ``BetterZoom`` as ``BaseZoomTool``
#. Copy ``BetterSelectingZoom`` into ``ZoomTool`` and delete old
   ``BetterSelectingZoom``, or delete old ``ZoomTool`` and rename
   ``BetterSelectingZoom`` as ``ZoomTool``
#. Decide on means for replacing ``RectZoom`` and ``TrackingZoom`` and with
   functionality on ``ZoomTool``

      * ``RectZoom`` currently just subclasses ``ZoomTool`` (aka
        ``BetterSelectingZoom``) and sets ``tool_mode = "box"`` / ``always_on = True``
      * ``TrackingZoom`` currently just subclasses ``ZoomTool`` (aka
        ``BetterSelectingZoom``) and defines a ``normal_mouse_wheel`` method.

#. Do the same for ``TrackingPanTool`` (which just subclasses ``PanTool`` and
   overrides ``_end_pan``).
#. Chose one of ``pan_tool.PanTool`` and ``pan_tool2.PanTool`` to be the go-to
   PanTool moving forawd. Update as needed / Delete the other.
#. Decide fate of ``BaseZoomTool`` in enable.
