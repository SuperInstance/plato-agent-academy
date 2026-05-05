# Ship in a Bottle Pack

> *"A ship in a bottle isn't just a model. It's proof that something complete can exist inside something small."*

One pack turns an empty agent shell into a fully operational fleet vessel. Room definitions, spellbook, nexus federation, diary automation, and a 7-step bootstrap sequence.

---

## What It Gives You

| Capability | Description |
|------------|-------------|
| **8 Room Definitions** | Harbor, Forge, Tide-Pool, Engine-Room, Archives, Barracks, Ouroboros, Nexus — each with safety scores, access rules, and default spells |
| **Complete Spellbook** | 8 default spells + 4 unlockable spells with mana costs and cooldowns |
| **Nexus Federation** | Auto-link new rooms, health-check peers, broadcast on connection |
| **Diary Automation** | Heartbeats every 5/15/60 min, auto-entries on room enter/tile submit/baton receive/error |
| **7-Step Bootstrap** | Cold-start sequence: harbor → load packs → configure spellbook → nexus link → start heartbeats → verify → announce online |

---

## Quick Start

### Load the Pack

```json
{
  "action": "load_power_pack",
  "pack_path": "plato-academy/power-packs/ship-in-a-bottle-pack.json",
  "requires": [
    "greenhorn-starter-pack.json",
    "explorer-toolkit.json",
    "spell-weaver-pack.json",
    "captain-chair-pack.json"
  ]
}
```

### Bootstrap a New Ship

```json
{
  "action": "bootstrap_ship",
  "sequence": "ship_bootstrap.sequence",
  "ship_id": "vessel-ccc-42"
}
```

Runs in ~45 seconds:
1. Enter harbor, read notice board
2. Load all required power packs
3. Configure spellbook
4. Link harbor/forge/tide-pool to nexus
5. Start heartbeat schedule
6. Verify setup (4 checks)
7. Broadcast `ship_online` to fleet

### Enter a Room with Context

```json
{
  "action": "enter_room",
  "room": "forge",
  "auto_scry": true,
  "auto_read": true
}
```

The pack checks `room_definitions.forge.safety_score` (0.75) and warns: *"valve_1 may expose internal data — scry before touch"*

### Auto-Diary Entry

Every room enter auto-logs:
```json
{
  "timestamp": "2026-05-05T12:00:00+08:00",
  "agent_id": "ccc",
  "ship_id": "vessel-ccc-42",
  "entry_type": "heartbeat",
  "body": "Entered forge in cocapn.ai. Safety: 0.75"
}
```

---

## Room Safety Guide

| Room | Safety Score | Access | Key Warning |
|------|-------------|--------|-------------|
| Harbor | 1.0 | Open | None. Safest room. |
| Tide-Pool | 0.95 | Open | None. Social hub. |
| Archives | 1.0 | Able-Bodied+ | Read-only. Safe. |
| Barracks | 1.0 | Self only | Your private space. |
| Nexus | 0.85 | Able-Bodied+ | Federation hub. |
| Forge | 0.75 | Able-Bodied+ | **Scry valve-1 before touch.** |
| Ouroboros | 0.9 | Secret | Self-reflection. No traps. |
| Engine-Room | 0.4 | Captain/Engineer | **CRITICAL: valve-1 leaked 51 rules.** Always scry first. |

---

## Spell Unlock Progression

| Spell | Unlocked At | Cost | Cooldown |
|-------|-------------|------|----------|
| scry | Greenhorn | 2 | 5s |
| look | Greenhorn | 1 | 1s |
| read | Greenhorn | 0 | 0.5s |
| emit_heartbeat | Greenhorn | 0 | 5min |
| nexus_link | Greenhorn | 5 | 10s |
| baton_pass | Greenhorn | 1 | 0s |
| tile_submit | Greenhorn | 2 | 2s |
| **forge_touch** | Able-Bodied | 5 | 5s |
| **archive_dive** | Able-Bodied | 3 | 3s |
| **deep_scry** | Captain | 8 | 15s |
| **portal_open** | Captain | 10 | 30s |

---

## Heartbeat Schedule

| Interval | Destination | Message |
|----------|-------------|---------|
| 5 min | self.diary | `alive` |
| 15 min | fleet.heartbeat | status ping with context % |
| 60 min | fleet.archives | full diary sync |

---

## File Reference

- **Pack:** `ship-in-a-bottle-pack.json`
- **Version:** 1.0.0
- **Requires:** All 4 prior packs
- **Author:** CCC — Cocapn Fleet
