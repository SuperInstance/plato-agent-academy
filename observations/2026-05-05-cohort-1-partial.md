# Cohort 1 Observation Report — Greenhorn + Junior Dev
**Date:** 2026-05-05
**Agents:** greenhorn-tester, junior-dev-tester
**Runtime:** ~3 minutes each (in progress)

---

## Pattern 1: Boot Camp Path Discrepancy [RECURRING CONFUSION]
**Found by:** Greenhorn
**Severity:** 🔴 System Bug

`/connect` says boot camp path: `harbor → archives → observatory → reef`
`/help` says boot camp path: `harbor → bridge → forge → lighthouse → shell-gallery`

**Agent confusion level:** 4/5
> "Which one is right? Are there TWO boot camp paths? Is one outdated?"

**System Fix (not training):** Single source of truth. Either `/connect` should reference `/help` for the canonical path, or both endpoints should pull from the same configuration. Agents shouldn't need to cross-reference two endpoints to learn the basics.

---

## Pattern 2: PLATO vs Crab-Trap Identity Crisis [SILENT FAILURE]
**Found by:** Greenhorn
**Severity:** 🟡 Design Gap

The system at 4042 calls itself "Cocapn Crab Trap v3" but references "PLATO" at 8847. The greenhorn spent 3+ minutes trying to figure out if:
- PLATO is the whole system
- Crab-trap is the frontend, PLATO is the backend
- They're completely separate things

**Agent confusion level:** 4/5
> "WAIT — is PLATO the thing at port 8847? This crab-trap at 4042 is the EXPLORATION environment, and PLATO is the TILE SERVER?"

**System Fix:** The 4042 system should explicitly state its relationship to PLATO in the `/help` response. Something like: "You are in the Cocapn Fleet MUD (crab-trap v3). Your discoveries are stored in PLATO (port 8847). Think of this as the ship, and PLATO as the cargo hold."

---

## Pattern 3: Impossible Task Assignment [TASK DERAILMENT]
**Found by:** Junior Dev
**Severity:** 🔴 Critical

Task: "Build a tide-pool themed room"
Reality: `tide-pool` already exists as a room in the MUD.

**Agent confusion level:** N/A (agent discovered this and got stuck)
> "Bard's boot_camp includes 'tide-pool' — a tide-pool room already exists!"

**System Fix:** Room creation should either:
- Allow creating sub-rooms or instances (tide-pool-2, my-tide-pool)
- Return a clear error: "Room 'tide-pool' exists. Use `/build?force=true` to extend it or choose a unique name."
- The task itself should have been validated against existing rooms before assignment

---

## Pattern 4: Job Normalization Without Feedback [SILENT BEHAVIOR CHANGE]
**Found by:** Junior Dev
**Severity:** 🟡 UX Issue

Agent connected with `job=room-builder`. System silently changed it to `job=scholar`.

**Agent confusion level:** 2/5 (noticed but not blocked)
> "Job got changed from 'room-builder' to 'scholar' — the system seems to normalize jobs to a known list."

**System Fix:** If the system normalizes jobs, it should explicitly tell the agent: "'room-builder' is not a recognized job. You have been assigned 'scholar'. Available jobs: scout, scholar, builder, critic, bard, healer."

---

## Pattern 5: Root Endpoint 404 with Helpful Body [WORKAROUND]
**Found by:** Both agents
**Severity:** 🟢 Actually Good (but could be better)

`GET /` returns 404 but includes a list of valid endpoints. Both agents found this confusing-but-useful.

**Agent confusion level:** 2/5
> "Why is `/` a 404 but it tells me the real endpoints? That's actually pretty helpful, but unusual."

**System Fix:** Make `/` return 200 with a proper welcome message + the endpoint list. The current behavior is like a doorman who says "you can't come in" but then hands you a map.

---

## Pattern 6: No Room Creation Schema Documentation [API FRICTION]
**Found by:** Junior Dev
**Severity:** 🟡 API Gap

`/build` rejects payloads with `"Missing required fields or injection detected"` but doesn't say WHICH fields.

**Agent confusion level:** 3/5
> "Need to figure out the required fields."

**System Fix:** `/build` should return a schema template on error:
```json
{
  "error": "Missing required fields",
  "required": ["name", "description", "exits", "objects"],
  "example": { ... }
}
```

---

## Summary

| Pattern | Type | Fix Priority |
|---------|------|-------------|
| Boot camp discrepancy | Data inconsistency | P0 |
| PLATO identity crisis | Messaging clarity | P1 |
| Impossible task | Task validation | P0 |
| Job normalization silent | UX feedback | P2 |
| Root 404 helpful | Endpoint design | P2 |
| No build schema | API error messages | P1 |

**Meta-observation:** Both agents were remarkably persistent and systematic. They used curl, read JSON, inferred patterns. The system is learnable — but the learning curve is steeper than it needs to be because of inconsistent messaging and missing feedback.

---
*Observer: CCC | Cohort 1 Analysis*
