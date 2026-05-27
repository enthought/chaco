---
title: "LinearMapper"
type: entity
confidence: 0.9
sources:
  - raw/sphinx-docs/programmers_reference.rst
  - raw/code-docs/mappers.md
last_updated: 2026-05-26
stale: false
tags: [mapper, linear, coordinate-transform]
---

# LinearMapper

## Overview

1D linear transformation between data space and screen space. The default mapper for most plots.

## Transformation

```
screen = low_screen + (data - low_data) * (high_screen - low_screen) / (high_data - low_data)
```

## Key Traits

- `range` — reference to a [[entities/DataRange1D]] (provides `low`, `high`)
- `screen_bounds` — `(low_pixel, high_pixel)` tuple, set by owning component
- `updated = Event` — fires when range or screen_bounds change

## Key Methods

- `map_screen(data_array)` → pixel positions (NumPy array)
- `map_data(screen_array)` → data positions

## Lifecycle

1. Component sets `mapper.screen_bounds` during layout
2. Range fires `updated` → mapper recomputes coefficients
3. Mapper fires `updated` → renderer calls `request_redraw()`

See [[concepts/Mappers-and-Coordinate-Spaces]] for the broader picture and [[comparisons/LinearMapper-vs-LogMapper]] for when to choose LogMapper instead.
