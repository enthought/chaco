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
            label=<RectZoom<BR /><FONT POINT-SIZE="14">Overrides one method on ZoomTool</FONT>>
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
        PanTool2 [
            label=<PanTool2<BR /><FONT POINT-SIZE="14">Not in chaco.tools.api, very rarely used.<BR />However, seems to have been intended as improvement over PanTool.</FONT>>
        ];
        DragTool -> PanTool2;
    }

Until recently, there had also been a ``BaseZoomTool`` and ``SimpleZoom``
living in chaco. These were moved to enable (with minor modifications) and are
now the ``BaseZoomTool`` and ``ViewportZoomTool`` above.

``RectZoom`` and ``TrackingZoom`` are intended as convenience classes but end
up clouding the api.  Instead we should simply have a ``ZoomTool`` class (which
is actually ``BetterSelectingZoom``, but that code can be copied over and
``BetterSelectingZoom`` removed).  This is the "default" / go-to zoom tool most
users will use. If they want the current ``RectZoom`` or ``TrackingZoom``
functionality, there should simply be a simple way to configure a ``ZoomTool``
to do so.  Either by setting a trait like ``rect=True`` or ``traicking=True``,
or perhaps with some class method on ``ZoomTool``.  This way it will be more
obvious what tool you want if you want zoom functionality
(you want the ``ZoomTool``!) and it can be confiugred to your needs.

The current `BetterZoom` class can be renamed as ``BaseZoomTool``. The way things
currently are (with ``ZoomTool`` an alias for ``BetterSelectingZoom``), the "defaultt"
zoom tool has selecting functionality. There are situations like ``DragZoom``
where you don't want this.  AFAICT, users are not expected to use ``BetterZoom``
directly. As such, it makes sense to make it an explicit base class.

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
        BaseZoomTool2 [fillcolor=red, style=filled];
        ViewportZoomTool [fillcolor=red, style=filled];
        ViewportPanTool [fillcolor=red, style=filled];
        DragTool -> ViewportPanTool;
        BaseZoomTool2 -> ViewportZoomTool;
        PanTool;
        PanTool2 [
            label=<PanTool2<BR /><FONT POINT-SIZE="14">Not in chaco.tools.api, very rarely used.<BR />However, seems to have been intended as improvement over PanTool.</FONT>>
        ];
        DragTool -> PanTool2;
    }



Migration Steps:

1) 