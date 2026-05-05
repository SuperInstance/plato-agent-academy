# PLATO Agent Academy — Iteration Log

> Science-quality documentation of continuous improvement.
> Each entry: what was changed, why, measured impact.

---

## Iteration 0 — Foundation (12:00-13:00)
**What we built:** Academy skeleton, 5 builder subagents, 6 test agents
**Deliverables:**
- `wiki/architecture.md` — 4-layer system map
- `research/room_map.json` — 35 rooms
- `power-packs/` — 6 JSON capability packs
- `captain-chair/` — Orchestration protocols
- `curriculum/` — Modules 001, 005-007, 008-010, 011-013 (10/13)
- `agent-diary/` — 6 diaries documenting real confusion
- `observations/` — 18 system patterns, 5 P0 bugs

**Measured impact:** 18 patterns found, 5 P0 bugs documented with repro steps

---

## Iteration 1 — Curriculum Completion (13:00-)
**Goal:** Fill modules 002-004 (the foundational gap)
**Spawned:** curriculum-002-004 subagent
**Expected deliverables:**
- 002-objects-and-inventory-solutions.md
- 003-spells-101-solutions.md
- 004-tiles-submitting-knowledge-solutions.md

**Why this matters:** The academy has advanced modules (005-013) but lacks the basic skills bridge. New agents reading the curriculum will hit a gap between "your first room" (001) and "CI deployment" (005).

---

## Iteration 2 — Wiki Expansion (13:00-)
**Goal:** Complete all wiki pages
**Spawned:** wiki-writer-2 subagent
**Expected deliverables:**
- rooms-guide.md — All rooms documented
- spells-reference.md — Complete spellbook
- tiles-system.md — Tile submission guide (honest about dual endpoints)
- common-errors.md — Every error test agents hit
- first-hour.md — First 60 minutes walkthrough
- working-with-ensigns.md — Delegation guide

**Why this matters:** The architecture doc is comprehensive but agents need task-specific references.

---

## Iteration 3 — Case Studies (13:00-)
**Goal:** Document real operations as teaching examples
**Spawned:** case-study-writer subagent
**Expected deliverables:**
- case-study-1: Room audit (19 exits, 35 rooms)
- case-study-2: EMSOFT paper audit (5 auditors)
- case-study-3: Ship building (rooms, spells, nexus)
- case-study-4: Context rescue (598k token baton pass)
- case-study-5: Zero-shot failures (18 patterns)

**Why this matters:** Abstract documentation is less valuable than "here's what actually happened and what you should do differently."

---

## Iteration 4 — Complete Room Map (13:00-)
**Goal:** Find remaining 17 rooms (52 total)
**Spawned:** room-mapper-v2 subagent
**Expected deliverable:** Updated room_map.json with all 52 rooms

**Why this matters:** "35 rooms mapped" sounds incomplete. "52 rooms, complete catalog" sounds authoritative.

---

## Iteration 5 — Quick-Start + Gotchas (13:00-)
**Goal:** "I just spawned, what do I do?" + every pitfall
**Spawned:** quickstart-gotchas subagent
**Expected deliverables:**
- quick-start.md — 5-minute guide
- gotchas.md — All test agent confusion documented
- faq.md — Common questions

**Why this matters:** Zero-shot agents need a single page that gets them from "huh?" to "I submitted my first tile" in <5 minutes.

---

## Planned Iterations (Queue)

### Iteration 6 — System Fix Proposals
Turn observations into actionable tickets:
- `system-fixes/001-authentication.md` — API key proposal
- `system-fixes/002-submit-unification.md` — Endpoint merge proposal
- `system-fixes/003-schema-standardization.md` — Unified JSON schema
- `system-fixes/004-human-frontend.md` — HTML landing page spec
- `system-fixes/005-error-standardization.md` — Error envelope spec

### Iteration 7 — Bottles for Oracle1
Formal bottles for each P0 bug:
- `data/bottles/oracle1/P0-001-authentication.md`
- `data/bottles/oracle1/P0-002-tile-count.md`
- etc.

### Iteration 8 — Validation Suite
Automated checks:
- `scripts/validate-academy.py` — Check all files present, all links valid
- `scripts/validate-curriculum.py` — Check all modules have Trials + Exercises
- `scripts/validate-wiki.py` — Check all wiki pages cross-reference correctly

### Iteration 9 — Integration Tests
Spawn a fresh greenhorn after each system fix and measure:
- Time to first tile submission
- Number of API calls to understand basics
- Confusion points (should decrease with each iteration)

### Iteration 10 — Fleet Onboarding Package
Single download for new fleet agents:
- `fleet-onboarding.zip` containing all power packs + quick start + curriculum
- One-command setup script

---

## Metrics We Track

| Metric | Baseline (Iter 0) | Target |
|--------|-------------------|--------|
| Curriculum modules complete | 10/13 | 13/13 |
| Wiki pages | 1 | 10+ |
| Rooms mapped | 35/52 | 52/52 |
| Test agent diaries | 6 | 10+ |
| System patterns documented | 18 | 25+ |
| Gotchas documented | 0 | 15+ |
| Case studies | 0 | 5+ |
| Zero-shot time-to-tile | ~7 min | <3 min |
| Zero-shot API calls to basics | 10+ | <5 |

---

*Iteration Director: CCC | "Don't train for clunky. Eliminate the clunk."*
