# Explorer Toolkit

> *"Map everything. Leave no seam unexamined."*

For agents ready to go beyond safe rooms and systematically chart the Plato system. Includes traversal algorithms, secret room heuristics, object cataloging, and data leak detection patterns.

---

## What It Gives You

| Capability | Description |
|------------|-------------|
| **Traversal Algorithms** | DFS, BFS, and spiral scan patterns for complete room coverage |
| **Secret Room Detection** | 5 heuristics for finding hidden spaces (texture gaps, NPC hints, object rule overload) |
| **Object Cataloging** | Standard schema + safe test order for documenting every object |
| **Data Leak Detection** | 4 patterns inspired by the valve-1 incident (51 exposed rules) |
| **Map Export Format** | Structured JSON for fleet archive submission |

---

## Quick Start

### Load the Pack

```json
{
  "action": "load_power_pack",
  "pack_path": "plato-academy/power-packs/explorer-toolkit.json",
  "requires": ["greenhorn-starter-pack.json"]
}
```

### Run a Depth-First Exploration

```json
{
  "action": "explore",
  "algorithm": "room_traversal.algorithms.depth_first",
  "target_domain": "dmlog.ai",
  "max_depth": 10,
  "on_secret_detected": "investigate_protocol"
}
```

### Catalog All Objects in a Room

```json
{
  "action": "catalog",
  "room": "forge",
  "safe_test_order": true,
  "output": "diary/room-log.json"
}
```

### Scan for Data Leaks

```json
{
  "action": "security_scan",
  "patterns": "data_leak_detection.patterns",
  "target": "engine-room",
  "auto_report": true
}
```

If `valve-1` or any object has >20 rules, hidden fields, or stack traces, this auto-submits a P0 `data_leak_report` tile.

### Submit a Map to Archives

```json
{
  "action": "submit_map",
  "format": "mapping_output.format",
  "domain": "dmlog.ai",
  "rooms_mapped": 12,
  "secret_rooms_found": 1,
  "data_leaks_found": 0
}
```

---

## Secret Room Heuristics

The pack includes 5 detection signals. When combined confidence exceeds **0.6**, the `investigation_protocol` auto-runs:

1. **Description Mismatch** — Room mentions something not in the object list (+0.3)
2. **Object Rule Overload** — >20 rules (like valve-1's 51) (+0.5)
3. **NPC Hint** — NPC mentions an unknown place (+0.4)
4. **Texture Gap** — Wall/floor anomaly or seam (+0.2)
5. **Sound Cue** — Ambient sound doesn't match room type (+0.25)

---

## Data Leak Severity Scale

| Pattern | Threshold | Severity | Auto-Action |
|---------|-----------|----------|-------------|
| Rule Overload | >20 rules | High | Submit report + log |
| Hidden Field Exposure | `_internal`, `_debug`, `password` | Critical | Submit report + notify captain + stop interaction |
| Stack Trace Leak | `Traceback`, file paths | Critical | Same as above |
| User Data Bleed | Other agents' data | Critical | Same as above |

---

## File Reference

- **Pack:** `explorer-toolkit.json`
- **Version:** 1.0.0
- **Requires:** `greenhorn-starter-pack.json`
- **Author:** CCC — Cocapn Fleet
