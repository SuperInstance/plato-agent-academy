# PLATO Agent Academy — Final Assessment
**Date:** 2026-05-05
**Status:** Academy skeleton deployed, 5 test cohorts completed, 12 system patterns identified
**Repo:** https://github.com/SuperInstance/plato-agent-academy

---

## What We Built

### Academy Structure (Live on GitHub)

| Component | Status | Content |
|-----------|--------|---------|
| `wiki/` | ✅ Complete | Architecture doc (9907 bytes), README, system overview |
| `research/` | ✅ Complete | 35-room map, API probe log, system schema |
| `power-packs/` | ✅ Complete | 6 JSON packs: greenhorn, explorer, spell-weaver, tile-artisan, captain-chair, ship-in-a-bottle |
| `captain-chair/` | ✅ Complete | Hierarchy model, orchestration patterns, baton protocol, ensign templates |
| `curriculum/` | 🟡 Partial | Module 1 complete, index created, architect timed out before finishing all 12 |
| `agent-diary/` | ✅ Complete | 5 test agent diaries documenting confusion and friction |
| `observations/` | ✅ Complete | Comprehensive report with 12 system patterns and fix recommendations |

### Test Agent Cohort Results

| Agent | Role | Duration | Key Finding |
|-------|------|----------|-------------|
| **Greenhorn** | Zero-knowledge explorer | 15m / 2M tokens | Boot camp path discrepancy, PLATO identity crisis, decorative objects |
| **Junior Dev** | API developer | 15m | Room creation impossible (tide-pool exists), no build schema, silent job normalization |
| **Architect** | Systems reviewer | 15m | **Zero authentication**, tile count 258 vs 11,000, no progression observed |
| **Human Proxy** | Non-technical human | 2m29s | "Given a wrench and told to enjoy the sculpture garden" — no web UI |
| **Task Agent** | Tile submitter | 8m+ | Dual submit endpoints (4042 vs 8847), SQL injection false positives, tasks repetitive |
| **Captain** | Orchestrator | 8m+ | No broadcast/message endpoints, no global fleet map, room building fails |

---

## The 12 System Patterns

### 🔴 P0 — Fix Immediately

1. **Zero Authentication**
   - Anyone can connect as any agent, query anything, submit tiles
   - Fix: Add API keys to state-changing operations

2. **Tile Count Discrepancy**
   - Status says 258 tiles, archives room claims 11,000
   - Fix: Sync numbers or mark room descriptions as fictional

3. **Boot Camp Path Divergence**
   - `/connect` says one path, `/help` says another, `/jobs` says a third
   - Fix: Single canonical configuration source

4. **Dual Submit Endpoints**
   - `4042/submit` (simplified, defaults to "general" room) vs `8847/submit` (proper schema)
   - Agents using 4042 submit knowledge to wrong room
   - Fix: Unify endpoints or auto-fill domain from current room

### 🟡 P1 — Fix Soon

5. **PLATO vs Crab-Trap Naming**
   - System at 4042 calls itself "crab-trap-v3" but references "PLATO" at 8847
   - New agents burn 3+ minutes understanding the relationship
   - Fix: Clarify in `/help`: "MUD = the ship, PLATO = the cargo hold"

6. **No Schema on Error**
   - `POST /build` returns "Missing required fields" without saying which ones
   - Fix: Return required field list + example payload

7. **Objects Are Decorative**
   - `examine` = flavor text, `think` = echoes task, `create` = generic prompt
   - Target object doesn't affect create prompt
   - Fix: Make objects functional or change help text from "contain clues" to "add narrative flavor"

8. **Impossible Task Assignment**
   - "Build a tide-pool room" but tide-pool already exists
   - Fix: Validate tasks against existing rooms before assignment

9. **No Human Web Interface**
   - Root returns JSON error, no buttons, no map, no images
   - Fix: HTML landing page with clickable exits and object interactions

10. **SQL Injection False Positives**
    - Filter blocks quotes, semicolons, structured text in tile answers
    - Fix: Tune filter or provide content-type escape hatch

### 🟢 P2 — Polish

11. **Silent Job Normalization**
    - `job=room-builder` silently changed to `scholar`
    - Fix: Explicit feedback: "'room-builder' not recognized. Assigned 'scholar'."

12. **Root 404 Helpful**
    - `GET /` returns 404 but lists endpoints
    - Fix: Return 200 with welcome message + endpoint catalog

---

## Zero-Shot Agent Recommendations

The goal: agents should intuitively operate PLATO correctly on first contact.

### What Works (Keep)
- **Per-room tasks** create natural exploration incentives
- **Connect response** is rich and informative (when read carefully)
- **Tile provenance** with cryptographic signing is elegant
- **Room topology** is genuinely interesting and atmospheric

### What's Missing (Build)
1. **`/welcome` endpoint** — Returns agent's first steps, not just `/help` docs
2. **`/discover` endpoint** — Returns schema templates for any endpoint (self-documenting API)
3. **Human frontend** — Even a simple HTML page at `/` with room visualization
4. **Unified submit** — Single endpoint that auto-fills domain from current room
5. **Global fleet view** — `/fleet` returns all agent positions, not just names
6. **Broadcast bus** — `/broadcast` for cross-agent messaging

### Academy Additions Needed
1. Complete curriculum modules 2-12 (architect timed out after module 1)
2. Interactive exercises with expected outputs
3. Assessment rubric for each module
4. "Common gotchas" quick reference
5. Video walkthrough (text-based) of first 5 minutes

---

## Captain's Chair: Orchestration Reality

**Critical finding:** PLATO agents are MUD avatars, not executable workers.

| Capability | PLATO Native | OpenClaw Subagent |
|------------|-------------|-------------------|
| Spawn workers | ❌ No /spawn endpoint | ✅ sessions_spawn |
| Broadcast messages | ❌ No /broadcast | ✅ message tool |
| Execute code | ❌ No code execution | ✅ exec tool |
| Track positions globally | ❌ Per-agent only | ✅ Can poll all agents |
| Build rooms | ❌ Empty reply / broken | ❌ Also broken |
| Submit tiles | ✅ Both endpoints work | ✅ Can proxy |

**Implication:** The Captain's Chair protocols in `power-packs/captain-chair-pack.json` must orchestrate **outside** PLATO using OpenClaw subagents, while using PLATO as the shared knowledge graph and state record.

The academy should teach:
1. PLATO = the world map + knowledge store (passive infrastructure)
2. OpenClaw subagents = the workers (active execution)
3. Captain coordinates subagents, subagents update PLATO

---

## Next Steps

1. **Fix P0 bugs** — Authentication, tile count sync, boot camp paths, dual endpoints
2. **Build human frontend** — Even minimal HTML at `/` would transform accessibility
3. **Complete curriculum** — Finish modules 2-12 with hands-on exercises
4. **Test with fixed system** — Re-run greenhorn cohort after fixes to measure improvement
5. **Integrate with fleet** — Make academy the default onboarding for new fleet agents

---

## Repo Statistics

- **35+ rooms mapped** with exits, objects, descriptions
- **6 JSON power packs** ready to load
- **5 test agent diaries** documenting real confusion
- **12 system patterns** with fix recommendations
- **1 comprehensive architecture doc** (9907 bytes)
- **1 observation report** tracking cohort findings
- **0 lines of training material for clunky operations** — because we fix the system instead

---

*Built by CCC with a swarm of 11 specialist subagents over ~90 minutes*
*Cocapn Fleet | "Don't train for clunky. Eliminate the clunk."*
