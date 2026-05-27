---
title: "Index-Value Model"
type: concept
confidence: 0.85
sources:
  - raw/sphinx-docs/architecture_overview.rst
  - raw/sphinx-docs/programmers_reference.rst
last_updated: 2026-05-26
stale: false
tags: [index, value, orientation, renderers]
---

# Index-Value Model

## Separation of Index and Value

Chaco renderers use "index" and "value" rather than "x" and "y":

- **Index** — the independent/domain variable (typically the axis you'd sweep)
- **Value** — the dependent/range variable (typically what's measured)

Each renderer has separate `index` and `value` data sources, mappers, and ranges.

## Orientation Independence

The mapping from index/value to screen X/Y is controlled by an `orientation` trait:

- `orientation = 'h'` — index maps to X, value maps to Y (default)
- `orientation = 'v'` — index maps to Y, value maps to X

This means the same renderer class can draw horizontal or vertical plots without code changes. Axes and grids also respect orientation.

## Why This Matters

- Shared index sources let multiple renderers (line + scatter on same domain) share a single pan/zoom
- Vertical bar charts reuse the same renderer as horizontal ones
- The distinction keeps the math clean: index mapper and value mapper are always separate objects with separate ranges
