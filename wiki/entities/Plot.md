---
title: "Plot"
type: entity
confidence: 0.9
sources:
  - raw/sphinx-docs/programmers_reference.rst
  - raw/code-docs/plot_class.md
last_updated: 2026-05-26
stale: false
tags: [plot, convenience, api]
---

# Plot

## Overview

`Plot` is the main convenience class for creating standard visualizations. It extends [[entities/PlotComponent]] and manages a single set of X/Y axes with multiple renderers sharing those axes.

## What It Wires Together

- A `PlotData` instance (string-keyed data dictionary)
- [[entities/ArrayDataSource]] instances (created automatically from PlotData)
- [[entities/DataRange1D]] for index and value
- [[entities/LinearMapper]] (or LogMapper) for index and value
- Renderers ([[entities/BaseXYPlot]] subclasses)
- Axes and grids ([[entities/AbstractOverlay]])

## Key API Methods

- `plot(("index_name", "value_name"), type="line", ...)` — add a line/scatter/bar renderer
- `img_plot("image_name", ...)` — add an image renderer
- `contour_plot("data_name", ...)` — add contour lines or filled contours
- `delplot("renderer_name")` — remove a renderer
- `plot_range` / `index_range` / `value_range` — access ranges directly

## When to Use Plot vs. Manual Composition

Use `Plot` for the common case of one X axis, one Y axis, and several overlaid datasets. For multi-axis, linked-plot dashboards, or non-standard layouts, compose [[entities/PlotComponent]], mappers, and containers directly.
