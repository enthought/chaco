---
title: "Chaco Overview"
type: concept
confidence: 0.9
sources:
  - raw/sphinx-docs/architecture_overview.rst
  - raw/sphinx-docs/introduction.rst
last_updated: 2026-05-26
stale: false
tags: [overview, architecture]
---

# Chaco Overview

Chaco is Enthought's 2D interactive plotting toolkit for Python, designed for building complex, linked visualizations rather than static charts. It sits atop a three-layer stack: [[entities/Kiva]] provides 2D vector drawing (analogous to Cairo), [[entities/Enable]] adds interactivity and layout with GUI toolkit bridging, and Traits supplies a reactive object system with type-checking and change notification. This stack means Chaco plots are live objects whose visual state updates automatically when data or parameters change.

The core architecture follows a data flow pipeline: PlotData → DataSources → Ranges → Mappers → Renderers (see [[concepts/Data-Flow-Pipeline]]). Components form a graph rather than a simple pipeline—shared ranges link multiple plots for synchronized panning/zooming, and tools mutate ranges to drive interaction. The math behind data transformations drives architectural modularity: each stage is independently replaceable.

Chaco is designed for subclassing, not just configuration. The class hierarchy provides abstract bases ([[entities/PlotComponent]], [[entities/BaseXYPlot]], [[entities/AbstractOverlay]]) that define protocols, with concrete implementations for common cases. The [[entities/Plot]] convenience class wires together axes, renderers, and data for the common single-X/Y-axis case, but power users compose primitives directly.

The toolkit includes renderers for line, scatter, image, contour, bar, candle, quiver, segment, polygon, and text plots. Containers (HPlotContainer, VPlotContainer, GridPlotContainer, OverlayPlotContainer) handle layout. Tools (PanTool, ZoomTool, inspectors) provide interaction via Enable's state-machine model. The scales system handles calendar/time axes.
