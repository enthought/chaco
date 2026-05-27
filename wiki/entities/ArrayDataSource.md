---
title: "ArrayDataSource"
type: entity
confidence: 0.9
sources:
  - raw/sphinx-docs/programmers_reference.rst
  - raw/code-docs/data_sources.md
last_updated: 2026-05-26
stale: false
tags: [data-source, array, numpy]
---

# ArrayDataSource

## Overview

The workhorse data source in Chaco. Wraps a single 1D NumPy array and provides change notification to downstream consumers (ranges, renderers).

## Key Interface

- `get_data()` → returns the underlying NumPy array
- `set_data(new_array)` → replaces data and fires `data_changed`
- `get_bounds()` → returns (min, max) tuple
- `data_changed = Event` — fired on `set_data()`, listened to by [[entities/DataRange1D]]
- `bounds_changed = Event` — fired when bounds change
- `metadata` dict — arbitrary key/value (selections, masks, etc.)

## Role in Pipeline

Sits between PlotData and [[entities/DataRange1D]] in the [[concepts/Data-Flow-Pipeline]]. Multiple renderers and ranges can reference the same ArrayDataSource instance, ensuring consistency.

## Related

- `GridDataSource` — 2D equivalent (pair of 1D arrays for structured grids)
- `FunctionDataSource` — lazily computed from a callable
- `ImageData` — 2D array for image plots
