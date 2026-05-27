---
title: "Data Flow Pipeline"
type: concept
confidence: 0.9
sources:
  - raw/sphinx-docs/architecture_overview.rst
  - raw/sphinx-docs/programmers_reference.rst
last_updated: 2026-05-26
stale: false
tags: [architecture, data-flow, pipeline]
---

# Data Flow Pipeline

## The Core Pipeline

```
PlotData → DataSources → Ranges → Mappers → Renderers → Plot
```

1. **PlotData** — Dictionary-like container mapping string names to raw arrays. Entry point for user data.
2. **DataSources** ([[entities/ArrayDataSource]]) — Wrap arrays with change notification (`data_changed` event) and metadata. Multiple renderers can share a single data source.
3. **Ranges** ([[entities/DataRange1D]]) — Track one or more data sources and compute bounds (low/high). Can be auto, fixed, or tracking.
4. **Mappers** ([[entities/LinearMapper]]) — Transform data coordinates to screen coordinates (and back). Driven by their range's bounds and the component's screen extent.
5. **Renderers** ([[entities/BaseXYPlot]]) — Draw data using Kiva primitives. Use mappers to convert data positions to pixel positions.

## Shared Ranges Link Plots

When multiple renderers or plots share the same Range object, they stay synchronized. Panning one plot updates the shared range, which fires `updated` on all connected mappers, which triggers `request_redraw()` on all connected renderers.

## How Pan/Zoom Works

```
PanTool/ZoomTool → modify Range low/high
                → Range fires 'updated'
                → Mapper recomputes transformation
                → Renderer invalidates and redraws
```

Tools never directly manipulate renderers—they only modify ranges. This decoupling means any number of renderers respond to a single tool's action.

## Side Branches

Mappers also drive:
- **Axes** — need mapper to place tick marks at correct screen positions
- **Grids** — same as axes, draw grid lines at tick positions

## Graph, Not Pipeline

The architecture is a directed graph. A single DataSource may feed multiple Ranges; a single Range may drive multiple Mappers (one per plot that shares it); tools connect to Ranges. The pipeline metaphor is a simplification of the most common path.
