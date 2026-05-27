---
title: "DataRange1D"
type: entity
confidence: 0.9
sources:
  - raw/sphinx-docs/programmers_reference.rst
  - raw/code-docs/ranges.md
last_updated: 2026-05-26
stale: false
tags: [range, bounds, auto-scaling]
---

# DataRange1D

## Overview

Tracks one or more [[entities/ArrayDataSource]] instances and computes bounds. Central to linked plots—sharing a DataRange1D synchronizes panning/zooming across renderers.

## Key Traits

- `low` / `high` — current effective bounds (read)
- `low_setting` / `high_setting` — one of:
  - `'auto'` — compute from data min/max
  - `'track'` — follow data with fixed window width
  - A float — fixed bound
- `margin` — fractional padding added to auto bounds (e.g., 0.05 = 5%)
- `sources` — list of data sources being tracked
- `updated = Event` — fires when bounds change

## Behavior

When any tracked source fires `data_changed`, DataRange1D recomputes bounds (if in auto mode) and fires `updated`. This drives [[entities/LinearMapper]] recalculation.

## Adding/Removing Sources

- `add(data_source)` — begin tracking
- `remove(data_source)` — stop tracking

## Pan/Zoom Integration

PanTool and ZoomTool modify `low_setting`/`high_setting` directly, switching from `'auto'` to fixed numeric values. This fires `updated`, propagating through the [[concepts/Data-Flow-Pipeline]].
