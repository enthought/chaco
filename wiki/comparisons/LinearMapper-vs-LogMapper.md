---
title: "LinearMapper vs LogMapper"
type: comparison
confidence: 0.85
sources:
  - raw/sphinx-docs/programmers_reference.rst
  - raw/code-docs/mappers.md
last_updated: 2026-05-26
stale: false
tags: [mapper, linear, logarithmic, comparison]
---

# LinearMapper vs LogMapper

## When to Use LinearMapper

- Data is uniformly distributed or spans a small range
- Most common case — used by default in [[entities/Plot]]
- Equal visual distance represents equal data distance

## When to Use LogMapper

- Data spans multiple orders of magnitude (e.g., 1e-3 to 1e6)
- You want to see detail in small values without losing large values
- Frequency spectra, exponential growth, power-law distributions

## Key Differences

| Aspect | [[entities/LinearMapper]] | LogMapper |
|--------|-------------|-----------|
| Transform | `screen = lerp(data, range, screen_bounds)` | `screen = lerp(log(data), log(range), screen_bounds)` |
| Zero handling | Works fine | Cannot map zero or negative values |
| Tick spacing | Uniform | Powers of 10 (or base) |
| Default | Yes | No — must explicitly set |

## Switching

In a [[entities/Plot]], swap mappers by setting:
```python
plot.index_mapper = LogMapper(range=plot.index_range)
```

Or use `Plot.index_scale = 'log'` if supported by the plot type.

## Gotchas

- LogMapper will error or produce NaN if range includes zero or negative values
- Ensure `DataRange1D.low` > 0 when using LogMapper
- Pan/zoom behavior feels different — panning in log space moves by multiplicative factors
