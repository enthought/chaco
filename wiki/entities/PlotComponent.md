---
title: "PlotComponent"
type: entity
confidence: 0.85
sources:
  - raw/sphinx-docs/architecture_overview.rst
  - raw/sphinx-docs/components_and_containers.rst
last_updated: 2026-05-26
stale: false
tags: [component, base-class, drawing]
---

# PlotComponent

## Overview

Subclass of Enable's `Component`. Base for all visual plot elements in Chaco. Defines a rectangular region that knows how to draw itself and receive events.

## Key Traits

- `bounds` — `[width, height]` in pixels
- `position` — `[x, y]` lower-left corner
- `padding` — space between outer bounds and plot area
- `overlays` — list of [[entities/AbstractOverlay]] drawn on top
- `underlays` — list of [[entities/AbstractOverlay]] drawn behind
- `tools` — list of attached tools (PanTool, ZoomTool, etc.)

## Drawing

Draws in layers (see [[concepts/Enable-Component-Model]]):
1. Background
2. Underlays (grids, etc.)
3. Main plot content (`_draw_plot()`)
4. Overlays (axes, legends, etc.)

## Event Handling

Receives normalized mouse/keyboard events from [[entities/Enable]]. Dispatches to attached tools first, then to overlays.

## `request_redraw()`

Marks the component as needing repaint. Propagates up through containers to the window, which schedules a





























redraw on the next event loop iteration.
