---
title: "Enable Component Model"
type: concept
confidence: 0.85
sources:
  - raw/sphinx-docs/architecture_overview.rst
  - raw/sphinx-docs/components_and_containers.rst
last_updated: 2026-05-26
stale: false
tags: [enable, components, containers, drawing, events]
---

# Enable Component Model

## Components

[[entities/Enable]]'s `Component` is a rectangular drawable region. [[entities/PlotComponent]] extends it for Chaco. Every component has:

- **Bounds** (`width`, `height`) and **position** (`x`, `y`)
- **Layered drawing** — background, underlay, main, overlay (drawn in that order)
- **Event handling** — receives mouse/keyboard events, can consume or pass through

## Containers

Containers are Components that hold child components and manage layout:

- `HPlotContainer` — horizontal arrangement
- `VPlotContainer` — vertical arrangement
- `GridPlotContainer` — grid layout
- `OverlayPlotContainer` — all children stacked at same position

Containers dispatch events to children (hit-testing by position) and aggregate draw calls.

## Layered Drawing

Each component draws in layers:

1. **Background** — fill color, border
2. **Underlays** — grids, background annotations ([[entities/AbstractOverlay]])
3. **Main layer** — the component's `_draw_plot()` (renderer content)
4. **Overlays** — axes, legends, cursors, selection highlights

Underlays and overlays are both instances of [[entities/AbstractOverlay]]—the distinction is only which list they're added to.

## Event Dispatch

Enable normalizes GUI toolkit events (wx, Qt, pyglet) into a common format. Events propagate from Window → top-level Container → children. Components with active tools get first crack at events. `request_redraw()` schedules a








repaint through the window.
