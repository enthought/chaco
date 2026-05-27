---
title: "Traits Reactivity"
type: concept
confidence: 0.85
sources:
  - raw/sphinx-docs/architecture_overview.rst
  - raw/sphinx-docs/event_handling.rst
last_updated: 2026-05-26
stale: false
tags: [traits, events, reactivity]
---

# Traits Reactivity

## Role in Chaco

Traits is the reactive object system underlying all Chaco objects. Every significant property (data arrays, range bounds, mapper parameters, visual styles) is a Trait, providing:

- **Type checking** — invalid assignments raise immediately
- **Change notification** — listeners fire when values change
- **Default values** — lazy initialization via `_trait_default()` methods

## Change Propagation

The `data_changed` / `bounds_changed` / `updated` events propagate through the [[concepts/Data-Flow-Pipeline]]:

```
ArrayDataSource.set_data() → fires data_changed
  → DataRange1D._data_updated() → recomputes low/high → fires updated
    → LinearMapper._range_updated() → fires updated
      → BaseXYPlot._mapper_updated() → calls invalidate() + request_redraw()
```

Each stage uses `on_trait_change` or `observe` to listen to its upstream dependency.

## Coupling Disjoint Components

Traits events couple objects that have no import-time dependency. A tool and a renderer never import each other—they both connect to a shared Range via trait listeners. This is core to Chaco's extensibility.

## Common Patterns

- `Event` traits (e.g., `data_changed = Event`) — fire-and-forget signals
- `Property` traits — computed values that cache and invalidate
- `on_trait_change(name)` decorators — register listeners
- `trait_setq` — suppress notifications during batch updates
