---
title: "Chaco Wiki Index"
type: index
confidence: 0.95
sources:
  - raw/sphinx-docs/architecture_overview.rst
last_updated: 2026-05-26
stale: false
tags: [index, navigation]
---

# Chaco Wiki

## Overview

- [[overview]] — High-level synthesis of Chaco's architecture and current state

## Concepts

- [[concepts/Data-Flow-Pipeline]] — Core pipeline: PlotData → DataSources → Ranges → Mappers → Renderers
- [[concepts/Traits-Reactivity]] — How Traits change notification drives interactivity
- [[concepts/Enable-Component-Model]] — Components, containers, layered drawing, event dispatch
- [[concepts/Index-Value-Model]] — Separation of index (domain) and value (range) in renderers
- [[concepts/Mappers-and-Coordinate-Spaces]] — Data space vs screen space transformations

## Entities

- [[entities/Plot]] — Convenience class wiring axes, renderers, and data together
- [[entities/ArrayDataSource]] — Workhorse data source wrapping a NumPy array
- [[entities/LinearMapper]] — 1D linear data↔screen transformation
- [[entities/DataRange1D]] — Auto-tracking 1D data bounds
- [[entities/AbstractOverlay]] — Base for overlays, underlays, axes, grids, legends
- [[entities/BaseXYPlot]] — Abstract base for index/value XY renderers
- [[entities/PlotComponent]] — Base class for all visual plot elements
- [[entities/Kiva]] — 2D vector drawing library (GraphicsContext, AGG, OpenGL)
- [[entities/Enable]] — Interactivity/layout layer bridging GUI toolkits

## Comparisons

- [[comparisons/LinearMapper-vs-LogMapper]] — Choosing between linear and logarithmic mapping
