---
title: "Kiva"
type: entity
confidence: 0.85
sources:
  - raw/sphinx-docs/architecture_overview.rst
  - raw/sphinx-docs/kiva_overview.rst
last_updated: 2026-05-26
stale: false
tags: [kiva, graphics, drawing, backend]
---

# Kiva

## Overview

2D vector drawing library analogous to Cairo or Quartz 2D. Provides the `GraphicsContext` that all Chaco rendering ultimately targets.

## GraphicsContext

The central object. Provides a state-machine drawing API:

- **Path operations** — `move_to()`, `line_to()`, `curve_to()`, `rect()`, `arc()`
- **Drawing** — `stroke_path()`, `fill_path()`, `draw_path()`
- **Text** — `show_text()`, `set_font()`
- **Images** — `draw_image()`
- **State** — `save_state()` / `restore_state()`, affine transforms, clipping

## Backends

- **AGG** (Anti-Grain Geometry) — software rasterizer, default, highest quality
- **OpenGL** — hardware-accelerated for large datasets
- **PDF/SVG** — vector output for publication
- **QPainter** — delegates to Qt's painter

## Role in Chaco

Renderers receive a `gc` (GraphicsContext) in their draw methods and issue Kiva calls to produce pixels. Kiva is below [[entities/Enable]] in the stack—Enable's Component.draw() passes the gc down.
