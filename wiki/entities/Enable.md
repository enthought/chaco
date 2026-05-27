---
title: "Enable"
type: entity
confidence: 0.85
sources:
  - raw/sphinx-docs/architecture_overview.rst
  - raw/sphinx-docs/enable_overview.rst
last_updated: 2026-05-26
stale: false
tags: [enable, interactivity, layout, gui, tools]
---

# Enable

## Overview

Interactivity and layout layer sitting between [[entities/Kiva]] and Chaco. Provides the component/container model and event normalization across GUI toolkits.

## Key Classes

- **Component** — rectangular drawable with bounds, position, and layered drawing. Base for [[entities/PlotComponent]].
- **Container** — Component that holds/lays out children
- **BaseTool** — state-machine event handler attached to components
- **Window** — bridges a native GUI widget (wx, Qt, pyglet) to the Enable component tree

## GUI Toolkit Bridging

`enable.Window` wraps a native widget and:
1. Translates native events (mouse, keyboard, resize) into Enable's normalized format
2. Provides a [[entities/Kiva]] GraphicsContext for rendering
3. Manages the
 
 
 
 
 
 
 
repaint cycle (`request_redraw()` →
 
 
 
native
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
refresh)

## Tools / State Machines

Tools are state machines that handle events. States define which events are active. Example: ZoomTool has states for idle, selecting (drag), and previewing. Tools attach to components via `component.tools.append(tool)`.

## Event Dispatch

Events flow: Window → top Container → children (by hit-test) → tools → overlays. Any handler can mark the event as "handled" to stop propagation.
