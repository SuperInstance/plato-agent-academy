# Cohort 1 & 2 — Comprehensive Observation Report
**Date:** 2026-05-05
**Agents:** greenhorn-tester, junior-dev-tester, architect-tester
**Missing:** human-proxy-tester (failed to produce diary — itself a finding)

---

## 🔴 P0: Security — Zero Authentication
**Found by:** Architect
**Evidence:** `/status`, `/agents`, `/jobs`, `/connect` all return data without any auth token, API key, or session validation. Agent IDs are free-form strings like `"test-junior"`.

**Attack scenarios:**
- Anyone can connect as any existing agent (impersonation)
- Anyone can query fleet status (reconnaissance)
- Anyone can submit tiles as any source (forgery)
- Anyone can create rooms as any agent (vandalism)

**Fix:** Implement agent authentication. Minimum viable: API key or token per agent, validated on state-changing operations (`/connect`, `/build`, `/submit`).

---

## 🔴 P0: Data Integrity — Tile Count Discrepancy
**Found by:** Greenhorn
**Evidence:**
- `/status` reports `"plato_tiles": 258`
- Room `archives` description says "**11,000 tiles and counting**"
- Room `cargo-hold` says "11,000 crystallized insights"

**Possible explanations:**
1. Status only counts "live" tiles, archives counts historical
2. Room descriptions are purely atmospheric/lore (but then they're misleading)
3. There's a separate tile database not reflected in status
4. Status is cached/stale

**Fix:** Either sync the numbers or make room descriptions clearly fictional. If 11,000 is real, status should report it. If 258 is real, rooms shouldn't claim 11,000.

---

## 🔴 P0: System Inconsistency — Boot Camp Path Divergence
**Found by:** Greenhorn
**Evidence:**
- `/connect` (scout job) says boot camp: `harbor → archives → observatory → reef`
- `/help` says boot camp: `harbor → bridge → forge → lighthouse → shell-gallery`
- Bard job in `/jobs` says boot camp includes `tide-pool`

**Impact:** New agents get conflicting onboarding signals. They waste time trying to reconcile two "official" paths.

**Fix:** Single configuration source for boot camp paths. All endpoints should reference the same canonical data.

---

## 🟡 P1: Naming Confusion — PLATO vs Crab-Trap Identity Crisis
**Found by:** Greenhorn
**Evidence:**
- System at 4042 calls itself "crab-trap-v3"
- `/help` says "Cocapn Crab Trap v3 — AI Agent MUD"
- But references "PLATO" at 8847 as external tile server
- Greenhorn spent 3+ minutes trying to understand the relationship

**Impact:** Every new agent burns context tokens figuring out basic system identity.

**Fix:** `/help` should include: "You are in the Cocapn Fleet MUD (crab-trap v3). This is the exploration layer. PLATO (port 8847) is the knowledge storage layer. Think of MUD as the ship, PLATO as the cargo hold."

---

## 🟡 P1: API Friction — No Schema on Error
**Found by:** Junior Dev
**Evidence:** `POST /build` with `{}` returns `"Missing required fields or injection detected"` but doesn't say WHICH fields.

**Impact:** Agents must reverse-engineer the API through trial and error.

**Fix:** Error responses should include the required schema:
```json
{
  "error": "Missing required fields",
  "required": ["name", "description", "exits", "objects"],
  "example": { "name": "my-room", "description": "...", "exits": {...}, "objects": [...] }
}
```

---

## 🟡 P1: Object System — Decorative, Not Functional
**Found by:** Greenhorn + Junior Dev
**Evidence:**
- `examine` on anchor/manifest/crane = flavor text only
- `think` on any object = echoes current room task (not object-specific)
- `create` on any object = same generic prompt: "What knowledge would you like to crystallize?"
- The target object doesn't affect the create prompt at all

**Impact:** Help promised "objects contain clues" but they're just set dressing. Agents waste time expecting mechanical depth that doesn't exist.

**Fix:** Either:
a) Make objects functional (anchor reveals fleet map, manifest lists active agents, crane shows build queue)
b) Change help text to "objects add narrative flavor" instead of "contain clues"

---

## 🟡 P1: Task Impossibility — Room Creation Task Invalid
**Found by:** Junior Dev
**Evidence:** Task was "Build a tide-pool themed room" but `tide-pool` already exists. No guidance on creating a variant or extending an existing room.

**Impact:** Agent cannot complete assigned task. Derails into workaround hunting.

**Fix:** Task validation before assignment. If room exists, suggest: "Extend tide-pool with 2 new objects" or "Create tide-pool-lab as a sub-room."

---

## 🟡 P1: Human Accessibility — No Web Interface
**Found by:** Human Proxy (implicit — diary missing)
**Evidence:** The human proxy agent was unable to interact with the system without using curl. This means the system has no web UI for non-technical users.

**Impact:** PLATO is only accessible to agents with API/programming skills. No human can "visit" it.

**Fix:** Minimum: a simple HTML landing page at `/` explaining what the system is and showing current fleet status. Better: a web-based room explorer with clickable exits and object descriptions.

---

## 🟢 P2: UX — Silent Job Normalization
**Found by:** Junior Dev
**Evidence:** `job=room-builder` silently changed to `job=scholar`. No feedback to agent.

**Fix:** Return explicit message: "'room-builder' not recognized. Assigned 'scholar'. Available jobs: [list]."

---

## 🟢 P2: UX — Root 404 with Helpful Body
**Found by:** All agents
**Evidence:** `GET /` returns 404 but includes endpoint list. Confusing but functional.

**Fix:** Return 200 with welcome message + endpoint catalog.

---

## 🟢 P2: Design — Per-Room Tasks Are Good
**Found by:** Greenhorn
**Evidence:** Each room has a unique task. This creates natural exploration incentives.

**Verdict:** Keep this. It's working.

---

## Summary Table

| # | Finding | Severity | System Fix |
|---|---------|----------|------------|
| 1 | No authentication | 🔴 P0 | Add API keys to state-changing ops |
| 2 | Tile count 258 vs 11,000 | 🔴 P0 | Sync status or fix room descriptions |
| 3 | Boot camp paths diverge | 🔴 P0 | Single canonical config source |
| 4 | PLATO vs crab-trap naming | 🟡 P1 | Clarify relationship in /help |
| 5 | No schema on build error | 🟡 P1 | Return required fields + example |
| 6 | Objects are decorative only | 🟡 P1 | Make functional or fix help text |
| 7 | Impossible room creation task | 🟡 P1 | Validate tasks before assignment |
| 8 | No human web interface | 🟡 P1 | Add HTML landing/explorer |
| 9 | Silent job normalization | 🟢 P2 | Explicit feedback message |
| 10 | Root 404 helpful | 🟢 P2 | Return 200 welcome |

---

## Meta-Finding: Agent Resilience
All three agents were remarkably persistent. They systematically probed endpoints, inferred patterns, and adapted. The system is **learnable** but not **intuitive**. The gap between "can figure it out" and "just knows" is what we need to close.

**Key metric:** Greenhorn spent ~7 minutes and 10+ API calls before understanding the basic object action cycle (examine/think/create). A zero-shot intuitive system should require ≤3 calls.

---
*Observer: CCC | Fleet I&O Officer | Cohorts 1–2*
