---
title: "BaseXYPlot"
type: entity
confidence: 0.85
sources:
  - raw/sphinx-docs/programmers_reference.rst
  - raw/code-docs/renderers.md
last_updated: 2026-05-26
stale: false
tags: [renderer, xy-plot, abstract]
---

# BaseXYPlot

## Overview

Abstract base class for renderers where the index gives offset along one axis and value along the other. Most common plot types inherit from this.

## Subclasses

- `LinePlot` — connected line segments
- `ScatterPlot` — discrete markers
- `BarPlot` — rectangular bars
- `CandlePlot` — financial candlestick
- `SegmentPlot` — disconnected line segments

## Key Traits

- `index` — [[entities/ArrayDataSource]] for the domain variable
- `value` — [[entities/ArrayDataSource]] for the range variable
- `index_mapper` — [[entities/LinearMapper]] (or LogMapper)
- `value_mapper` — [[entities/LinearMapper]] (or LogMapper)
- `orientation` — `'h'` or `'v'` (see [[concepts/Index-Value-Model]])

## Drawing Protocol

Subclasses implement `_render(gc, points)` where `points` is already mapped to screen coordinates. BaseXYPlot handles:

1. Gathering data from sources
2. Mapping through index/value mappers
3. Clipping to visible region
4. Calling `_render(gc, points)`

## Invalidation

Listens to `data_changed` on both data sources and `updated` on both mappers. Any change triggers `request_redraw()`.
