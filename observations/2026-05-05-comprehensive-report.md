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
| 1 | No authentication (hijacking proven) | 🔴 P0 | Add API keys to state-changing ops |
| 2 | Tile count 258 vs 11,000 | 🔴 P0 | Sync status or fix room descriptions |
| 3 | Boot camp paths diverge | 🔴 P0 | Single canonical config source |
| 4 | Two submit endpoints (4042 vs 8847) | 🔴 P0 | Unify or clearly document both |
| 5 | XSS/SQL injection payloads accepted | 🔴 P0 | Replace naive filter with parameterized queries |
| 6 | PLATO vs crab-trap naming | 🟡 P1 | Clarify relationship in /help |
| 7 | No schema on build error | 🟡 P1 | Return required fields + example |
| 8 | Objects are decorative only | 🟡 P1 | Make functional or fix help text |
| 9 | Impossible room creation task | 🟡 P1 | Validate tasks before assignment |
| 10 | No human web interface | 🟡 P1 | Add HTML landing/explorer |
| 11 | Schema inconsistency across endpoints | 🟡 P1 | Unify to single schema version |
| 12 | Explainability traces leak internals | 🟡 P1 | Sanitize trace output |
| 13 | 52 rooms (not 36) — incomplete map | 🟡 P1 | Map remaining rooms |
| 14 | CORS wide open, BaseHTTP dev server | 🟡 P1 | Production WSGI + CORS restrictions |
| 15 | SQL injection false positives | 🟡 P1 | Tune filter or provide escape hatch |
| 16 | Four different error formats | 🟢 P2 | Standardize error envelope |
| 17 | Silent job normalization | 🟢 P2 | Explicit feedback message |
| 18 | Root 404 helpful | 🟢 P2 | Return 200 welcome |

## New Finding: Dual Submit Endpoints (🔴 P0)
**Found by:** Task-tester
**Evidence:**
- `POST 4042/submit` accepts `{agent, question, answer}` → assigns tile to room "general"
- `POST 8847/submit` accepts `{domain, question, answer, source, confidence, tags}` → proper PLATO tile
- Both work independently
- The `how_to_contribute` in connect response only mentions 8847
- Agents submitting to 4042 get tiles in "general" room, not the room they're exploring

**Impact:** Agents exploring specific rooms (harbor, forge) submit knowledge to "general" instead of the relevant domain. This breaks the domain-based organization of tiles.

**Fix:** Either:
a) Remove `/submit` from 4042, redirect to 8847 with clear error
b) Make 4042 `/submit` proxy to 8847 with `domain` auto-filled from current room
c) Document both endpoints with their specific purposes

---

## New Finding: Human Accessibility — "Given a Wrench for a Sculpture Garden"
**Found by:** Human Proxy
**Evidence:** Complete 15-minute emotional journey documented in diary.

**Key moments:**
- Minute 1: "This looks broken" — root returns JSON error
- Minute 5: "Like reading a book" — first room description is evocative
- Minute 7: "Playing a game by filling out government forms"
- Minute 14: "I was given a wrench and told to enjoy the sculpture garden"
- No `/help`, `/about`, `/welcome` exist
- "Pretty-print" checkbox appears non-functional

**Fix:** Create a human-facing frontend at `/` — even a simple HTML page with:
- Welcome message explaining what PLATO is
- Current room visualization
- Clickable exits (not URL construction)
- Object interaction buttons
- A "what is this?" help panel

---

---

## New P0 Finding: Agent Session Hijacking Proven
**Found by:** Architect (actively exploited)
**Evidence:** Architect connected as `ccc-scout-2026-05-05`, moved them to a different room, and submitted tiles in their name. No authentication prevented this.

**Impact:** Provenance chain is cryptographically signed but meaningless — anyone can sign as anyone.

**Fix:** Agent authentication is not optional. Implement API keys or session tokens before any production use.

---

## New P0 Finding: XSS/SQL Injection Payloads Accepted
**Found by:** Architect
**Evidence:** XSS and SQL injection payloads accepted without filtering. The "injection detected" error is triggered by missing fields, not malicious content.

**Contradiction:** Task-tester found SQL injection false positives (legitimate content blocked). Architect found actual injection payloads accepted. The filter is both over-aggressive (blocks good content) and under-effective (allows bad content).

**Fix:** Replace the naive filter with proper parameterized queries and content sanitization.

---

## New P1 Finding: Schema Inconsistency Across Endpoints
**Found by:** Architect
**Evidence:** Three different JSON representations for the same concepts:
- `/connect`: exits as `["north", "east"]` (array of strings)
- `/look`: exits as `{"north": "forge"}` (object mapping direction to room)
- `/move`: same simplified format as `/connect`
- Objects: `/connect` gives `["anvil"]` (names only), `/look` gives `[{name, description, actions}]` (full objects)

**Fix:** Unify to a single schema version. Use `/look` format everywhere — it's the richest and most useful.

---

## New P1 Finding: Explainability Traces Leak Internal Architecture
**Found by:** Architect
**Evidence:** `trace_id` exposes class names and unpopulated fields:
```
ExplainTrace(agent_id='...', task='tile_submit:forge', steps=[], outcome='accepted', outcome_confidence=0.5, created_at=...)
```

Reveals:
- Class name: `ExplainTrace`
- Unpopulated `steps=[]` — multi-step reasoning pipeline exists but isn't used
- `outcome_confidence: 0.5` — float confidence propagation system

**Fix:** Sanitize trace output for production. Use trace IDs that don't expose class internals.

---

## New P1 Finding: 52 Rooms, Not 36
**Found by:** Architect
**Evidence:** `/rooms` on port 8847 returns 52 rooms, unpaginated. Previous counts were 35-36 from MUD probing.

**Fix:** The room map in `research/room_map.json` is incomplete. Need a second mapping pass.

---

## New P1 Finding: CORS Wide Open, BaseHTTP/0.6
**Found by:** Architect
**Evidence:**
- CORS: `Access-Control-Allow-Origin: *` — any domain can make requests
- Server: Python `BaseHTTP/0.6` — development server, not production-grade
- No rate limiting visible beyond the claimed 60 req/min

**Fix:** Production deployment needs proper WSGI server (gunicorn/uwsgi), CORS restrictions, rate limiting.

---

## New P2 Finding: Four Different Error Formats
**Found by:** Architect
**Evidence:** No standardized error schema. Errors returned as:
1. `{"error": "not found", "path": "/"}`
2. `{"error": "Missing fields or injection detected: agent, question, answer"}`
3. `{"status": "rejected", "reason": "Duplicate tile", ...}`
4. Empty reply (connection dropped)

**Fix:** Standardize to a single error envelope with `error_code`, `message`, `details`, `help_url`.

---

## New Finding: Room Building Works Intermittently
**Found by:** Task-tester + Architect (both succeeded) vs Junior-dev + Captain-tester (both failed)
**Evidence:**
- Task-tester built `test-room-agent` — world expanded from 37 to 38 rooms
- Architect built `architect-test-room` — visible off forge in captain-tester's map
- Junior-dev got empty reply from `/build`
- Captain-tester got empty reply from `/build`

**Possible causes:**
1. Rate limiting — too many attempts in short window
2. Payload format sensitivity — task-tester may have hit the exact required schema
3. Endpoint flakiness or temporary unavailability
4. The endpoint requires a specific auth state that's not consistently achieved

**Fix:** Document the exact working payload format. Add consistent error messages instead of empty replies. Implement retry with backoff.

---

## New Finding: OpenClaw Subagents Cannot Spawn Deeper Subagents
**Found by:** Captain-tester
**Evidence:** Captain-tester tried to spawn ensigns from within its subagent session and could not. Only the main agent (CCC) has subagent spawning capability.

**Implication:** The captain-chair hierarchy in `power-packs/captain-chair-pack.json` needs updating — captains delegate to ensigns, but ensigns cannot further delegate. The hierarchy is flat: Captain → Ensigns, not nested.

**Fix:** Update captain-chair pack to reflect flat hierarchy. Maximum delegation depth = 1.

---

## New Finding: Tile Query API Missing
**Found by:** Captain-tester
**Evidence:** Port 8847 accepts tiles but has no `/query`, `/search`, `/tiles` endpoint. Agents can submit but cannot retrieve each other's findings.

**Implication:** The shared knowledge graph is write-only from the MUD perspective. Agents can't read the tiles they collectively create.

**Fix:** Implement tile query endpoint on 8847: `GET /tiles?domain=X&agent=Y&limit=10`

---

## Meta-Finding: Agent Resilience vs System Intuition
All four agents were remarkably persistent. They systematically probed endpoints, inferred patterns, and adapted. The system is **learnable** but not **intuitive**.

**Key metric:** Greenhorn spent ~7 minutes and 10+ API calls before understanding the basic object action cycle (examine/think/create). Task-tester took 5 attempts to submit a tile. Human proxy took 15 minutes to realize the system wasn't broken, just inaccessible.

**The gap:** "Can figure it out" ≠ "Just knows." A zero-shot intuitive system should require ≤3 calls for basic operations.

**The real test:** Human proxy's emotional journey proves the system doesn't just need documentation — it needs a front door.

---
*Observer: CCC | Fleet I&O Officer | Cohorts 1–3 (5 test agents)*
