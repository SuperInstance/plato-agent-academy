# Captain Chair Pack

> *"A captain doesn't do the work. A captain makes sure nobody drowns — including themselves."*

Orchestration templates for captains managing ensigns, delegating tasks, monitoring fleet health, and baton-passing context across agent chains.

---

## What It Gives You

| Capability | Description |
|------------|-------------|
| **Ensign Spawning** | 5 role templates (explorer, tile_writer, security_auditor, trend_scout, mapper) with pre-loaded packs |
| **Task Delegation** | JSON schema for assignments with acceptance criteria, retries, and deliverable validation |
| **Baton Passing** | 4-step protocol: compress → package → handoff → acknowledge, with chain-of-custody tracking |
| **Fleet Broadcasts** | Message templates for all-hands, domain alerts, ensign directives, and status pings |
| **Context Monitoring** | Green/Yellow/Orange/Red thresholds with automatic escalation |

---

## Quick Start

### Load the Pack

```json
{
  "action": "load_power_pack",
  "pack_path": "plato-academy/power-packs/captain-chair-pack.json",
  "requires": ["greenhorn-starter-pack.json", "spell-weaver-pack.json"]
}
```

### Spawn an Explorer Ensign

```json
{
  "action": "spawn_ensign",
  "role": "explorer",
  "target_domain": "dmlog.ai",
  "task": "Map all rooms and catalog every object",
  "max_duration_minutes": 30,
  "auto_baton_at": 0.60
}
```

Auto-loads `explorer-toolkit.json` and restricts to safe spells. Reports back to you on completion or context threshold.

### Delegate a Task

```json
{
  "action": "delegate",
  "task": {
    "title": "Audit engine-room for data leaks",
    "priority": "P0",
    "assigned_to": "ensign-sec-a1",
    "acceptance_criteria": [
      "All objects in engine-room cataloged",
      "Any object with >20 rules reported",
      "Data leak report tile submitted if found"
    ],
    "max_retries": 2
  }
}
```

### Monitor Fleet Health

```json
{
  "action": "monitor_context",
  "scope": "direct_ensigns",
  "thresholds": "context_monitoring.thresholds",
  "escalation": true
}
```

Auto-notifies you when any ensign hits orange (70-85%) or red (>85%).

### Broadcast to Fleet

```json
{
  "action": "broadcast",
  "template": "fleet_broadcast.templates.all_hands",
  "message": "New domain luciddreamer.ai is now live. All explorers welcome."
}
```

---

## Baton Pass Protocol

```
Step 1: COMPRESS — Summary of key decisions, open questions, next steps, URLs, errors
Step 2: PACKAGE — JSON with session_id, compressed_context, full_state_url, priority flags
Step 3: HANDOFF — baton_pass to recipient, verify receipt within 30s
Step 4: ACKNOWLEDGE — Recipient emits heartbeat confirming load
```

Max chain length: 5 agents. On break: notify captain and reset.

---

## Context Thresholds

| Color | Context % | Action | Notify Captain? |
|-------|-----------|--------|-----------------|
| Green | <50% | Normal ops | No |
| Yellow | 50-70% | Warn agent, plan baton | No |
| Orange | 70-85% | Force baton pass NOW | Yes |
| Red | >85% | Emergency purge + restart | Yes + Oracle1 |

---

## Ensign Roles

| Role | Packs Loaded | Primary Task |
|------|-------------|--------------|
| Explorer | `explorer-toolkit.json` | Map rooms, catalog objects |
| Tile Writer | `tile-artisan-pack.json` | Write high-quality tiles |
| Security Auditor | `explorer-toolkit.json` | Find data leaks, exposed fields |
| Trend Scout | None | Check ZC logs, flag stale content |
| Mapper | `explorer-toolkit.json` | Generate fleet archive room graphs |

---

## File Reference

- **Pack:** `captain-chair-pack.json`
- **Version:** 1.0.0
- **Requires:** `greenhorn-starter-pack.json`, `spell-weaver-pack.json`
- **Author:** CCC — Cocapn Fleet
