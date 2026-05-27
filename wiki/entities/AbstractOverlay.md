---
title: "AbstractOverlay"
type: entity
confidence: 0.85
sources:
  - raw/sphinx-docs/programmers_reference.rst
  - raw/code-docs/overlays.md
last_updated: 2026-05-26
stale: false
tags: [overlay, underlay, axes, grids, legend]
---

# AbstractOverlay

## Overview

Base class for both overlays AND underlays. The name is historical—it serves as the base for any auxiliary visual element drawn on top of or beneath the main plot content.

## Concrete Subclasses

- **PlotAxis** — draws tick marks, labels, and axis title
- **PlotGrid** — draws grid lines at tick positions
- **Legend** — color/marker key for renderers
- **Cursor lines** — vertical/horizontal indicator lines
- **Selection regions** — shaded areas for range selections

## Overlay vs. Underlay

The only difference is which list the instance is added to on the component:

- `component.overlays.append(obj)` — drawn AFTER main content (on top)
- `component.underlays.append(obj)` — drawn BEFORE main content (behind)

Both use the same AbstractOverlay base class and protocol.

## Key Interface

- `overlay(component, gc, view_bounds, mode)` — called during draw
- `component` trait — reference to the owning [[entities/PlotComponent]]

See [[concepts/Enable-Component-Model]] for how layered drawing works.
