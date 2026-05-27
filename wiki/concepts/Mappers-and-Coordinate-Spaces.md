---
title: "Mappers and Coordinate Spaces"
type: concept
confidence: 0.85
sources:
  - raw/sphinx-docs/architecture_overview.rst
  - raw/sphinx-docs/programmers_reference.rst
last_updated: 2026-05-26
stale: false
tags: [mappers, coordinates, data-space, screen-space]
---

# Mappers and Coordinate Spaces

## Two Spaces

- **Data space** — the coordinate system of the actual data (e.g., 0–100 seconds, 1e-3–1e6 volts)
- **Screen space** — pixel coordinates within the component's bounds

Mappers transform between them.

## AbstractMapper Interface

- `map_screen(data_array)` → screen coordinates (NumPy array)
- `map_data(screen_array)` → data coordinates
- `range` trait — reference to a [[entities/DataRange1D]] (provides data bounds)
- `screen_bounds` — pixel extent (set by the owning component)
- `updated` event — fires when transformation changes

## Mapper Types

| Mapper | Use Case |
|--------|----------|
| [[entities/LinearMapper]] | Default. Linear interpolation between range bounds and screen bounds. |
| LogMapper | Logarithmic scale. Data spanning orders of magnitude. See [[comparisons/LinearMapper-vs-LogMapper]]. |
| GridMapper | 2D mapping (wraps two 1D mappers). Used by image/contour plots. |
| ColorMapper | Maps scalar data values to RGBA colors. Used by colormapped image/scatter plots. |

## How Ranges Drive Mappers

When a range's `low` or `high` changes (from auto-scaling, pan, or zoom), it fires `updated`. The mapper listens, recomputes its linear (or log) coefficients, and fires its own `updated` event, causing connected renderers to redraw.

## Screen Bounds

The component sets `mapper.screen_bounds` during layout (from its own `bounds` and `position`). Resizing the window propagates through this path.
