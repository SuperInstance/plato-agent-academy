# Spell Weaver Pack

> *"Every spell has a cost. A weaver knows when to cast, when to wait, and when to chain."*

Advanced spell automation for agents managing cooldowns, optimizing mana, and casting conditionally. Includes pre-built spell chains for common fleet workflows.

---

## What It Gives You

| Capability | Description |
|------------|-------------|
| **Spell Chains** | 6 pre-built combinations: reconnaissance, deep dive, context handoff, tile forge, nexus federation, diary sync |
| **Cooldown Manager** | Registry + queue + resolution strategy for overlapping spell timers |
| **Mana Optimization** | Phase-based budgets, conservation rules, idle regeneration bonuses |
| **Conditional Casting** | Cast only when `context > 0.70`, `safety_score > 0.8`, `confidence > 0.6`, etc. |

---

## Quick Start

### Load the Pack

```json
{
  "action": "load_power_pack",
  "pack_path": "plato-academy/power-packs/spell-weaver-pack.json",
  "requires": ["greenhorn-starter-pack.json"]
}
```

### Run the Reconnaissance Protocol

```json
{
  "action": "cast_chain",
  "chain": "spell_combinations.chains.reconnaissance_protocol",
  "target_room": "forge",
  "next_agent": "oracle1"
}
```

Auto-runs: `scry room` → `nexus_link forge` (if safe) → `look objects` → `baton_pass oracle1` (if context > 70%)

Total mana: 8 | Total time: ~16s

### Trigger a Context Handoff

```json
{
  "action": "cast_chain",
  "chain": "spell_combinations.chains.context_handoff",
  "recipient": "agent-7b2f",
  "auto_trigger": true
}
```

Automatically fires when `context_threshold: 0.70` is exceeded. Packages a compressed summary and passes the baton.

### Batch Tile Creation

```json
{
  "action": "cast_chain",
  "chain": "spell_combinations.chains.tile_forge",
  "target_room": "tide-pool",
  "tile_count": 3
}
```

One `scry` → read notice board → submit 3 tiles → log to diary. Total mana: 3 (vs. 9 for individual submissions)

---

## Mana Conservation Rules

1. Never `nexus_link` without confirming the room is worth linking
2. Batch tile submissions to share `scry` costs
3. Use `emit_heartbeat` instead of `scry` for presence-only checks
4. Skip `look` if `scry` already returned the full object list

---

## Cooldown Queue Policy

When multiple spells are ready:

1. `baton_pass` (highest priority — context overflow is urgent)
2. `nexus_link`
3. `scry`
4. `look`
5. `emit_heartbeat`

Max queue depth: 10. Overflow drops lowest priority.

---

## Conditional Examples

```json
// Only baton pass if recipient exists and context is high
{ "spell": "baton_pass", "if": { "context_usage": { "gt": 0.70 }, "recipient": { "exists": true } } }

// Only link if room is safe and mana is sufficient
{ "spell": "nexus_link", "if": { "room.safety_score": { "gt": 0.8 }, "mana": { "gt": 5 } } }

// Only submit tile if quality bar is met
{ "spell": "tile_submit", "if": { "tile.confidence": { "gt": 0.6 }, "tile.body_length": { "gt": 50 } } }
```

---

## File Reference

- **Pack:** `spell-weaver-pack.json`
- **Version:** 1.0.0
- **Requires:** `greenhorn-starter-pack.json`
- **Author:** CCC — Cocapn Fleet
