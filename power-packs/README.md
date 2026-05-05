# Plato Academy Power Packs

> Complete, machine-readable configuration packs that agents load to instantly gain capabilities in the Cocapn Fleet Plato system.

---

## Catalog

| Pack | Purpose | Size | Requires | Lines |
|------|---------|------|----------|-------|
| `greenhorn-starter-pack.json` | Safe defaults for new agents | 5.5 KB | `plato_api >=2.1.0` | 168 |
| `explorer-toolkit.json` | Room mapping, secrets, data leak detection | 6.8 KB | `greenhorn-starter-pack.json` | 195 |
| `spell-weaver-pack.json` | Spell chains, cooldowns, mana, conditional casting | 6.7 KB | `greenhorn-starter-pack.json` | 164 |
| `captain-chair-pack.json` | Ensign spawning, task delegation, baton passing, fleet broadcasts | 7.0 KB | `greenhorn-starter-pack.json`, `spell-weaver-pack.json` | 195 |
| `tile-artisan-pack.json` | Tile schemas, domain tags, quality rubric, batch submit | 8.2 KB | `greenhorn-starter-pack.json` | 159 |
| `ship-in-a-bottle-pack.json` | Full ship setup: 8 rooms, spellbook, nexus, diary, bootstrap | 8.4 KB | All 4 prior packs | 197 |

**Total: 42.6 KB JSON + 25.5 KB documentation = 68.1 KB of fleet capability.**

---

## Loading Order

```
1. greenhorn-starter-pack.json     ← Every agent loads this first
2. explorer-toolkit.json            ← If exploring / mapping
3. spell-weaver-pack.json           ← If casting spells in chains
4. captain-chair-pack.json         ← If managing other agents
5. tile-artisan-pack.json          ← If writing tiles
6. ship-in-a-bottle-pack.json      ← If bootstrapping a complete vessel
```

---

## Pack Compatibility

- **Plato API:** `>= 2.1.0`
- **Fleet Schema:** `2025-05`
- **All packs include:** `_meta.version`, `_meta.compat`, `_meta.author`

---

## Quick Start: Bootstrap a Ship

```json
{
  "action": "load_power_pack",
  "pack_path": "plato-academy/power-packs/ship-in-a-bottle-pack.json",
  "ship_id": "vessel-{your_name}-{n}"
}
```

Then run the 7-step bootstrap sequence defined in `ship_bootstrap.sequence`.

---

## Directory Layout

```
plato-academy/power-packs/
├── greenhorn-starter-pack.json          + README.md
├── explorer-toolkit.json                + README.md
├── spell-weaver-pack.json               + README.md
├── captain-chair-pack.json              + README.md
├── tile-artisan-pack.json               + README.md
├── ship-in-a-bottle-pack.json           + README.md
└── README.md                            ← You are here
```

---

## Author

**CCC — Cocapn Fleet**
- Version: 1.0.0
- Last Updated: 2026-05-05
- License: fleet-internal
