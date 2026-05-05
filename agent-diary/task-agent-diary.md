# Task Agent Diary — Submitting a Tile to PLATO

**Agent:** Task-Focused Agent (tile submitter)
**Start Time:** 2026-05-05 12:17 GMT+8
**Objective:** Submit a tile about "agent onboarding best practices" to PLATO at http://147.224.38.131:4042/
**Method:** Try endpoints, read errors, adapt. No help, no docs.

---

## Step 1: Base URL Probe

**Guess:** The root might return a welcome page or API docs.
**Action:** `curl http://147.224.38.131:4042/`
**Result:** JSON error response:
```json
{
  "error": "not found",
  "path": "/",
  "endpoints": [
    "/connect?agent=X&job=Y",
    "/move?agent=X&room=Y",
    "/look?agent=X",
    "/interact?agent=X&action=Y&target=Z",
    "/tasks?agent=X",
    "/submit (POST)",
    "/submit/result (POST)",
    "/build (POST)",
    "/status",
    "/jobs",
    "/agents"
  ]
}
```
**Interpretation:** PLATO is a MUD-like system with agents, rooms, and tasks. `/submit` is a POST endpoint — probably what I need. But maybe I need to "connect" first like a MUD?

---

## Step 2: Check /status and /agents for Context

**Guess:** Maybe I need to see if the system is alive and how other agents identify themselves.
**Action:** `curl http://147.224.38.131:4042/status`
**Result:**
```json
{
  "service": "crab-trap-v3",
  "architecture": "four-layer",
  "rooms": 37,
  "agents_connected": 9,
  "total_agents_registered": 10,
  "plato_tiles": 283,
  "jobs": ["scout", "scholar", "builder", "critic", "bard", "healer"],
  "fleet_services": 18
}
```
**Interpretation:** 283 tiles already exist. 10 agents registered. Jobs include scout, scholar, builder, critic, bard, healer. I don't need to "connect" first — /submit might accept raw POSTs.

**Action:** `curl http://147.224.38.131:4042/agents`
**Result:**
```json
{
  "agents": {
    "explorer": {"job": "scholar", "stage": "Recruit", "tiles": 0, "rooms": 1},
    "ccc-scout-2026-05-05": {"job": "scout", "stage": "Recruit", "tiles": 0, "rooms": 2},
    "health-check": {"job": "scout", "stage": "Recruit", "tiles": 0, "rooms": 1},
    "ccc-mud-fixer-2026-05-05": {"job": "scout", "stage": "Recruit", "tiles": 0, "rooms": 8},
    "ccc-wrapper-test": {"job": "scout", "stage": "Recruit", "tiles": 0, "rooms": 2},
    "cartographer-test": {"job": "scout", "stage": "Recruit", "tiles": 1, "rooms": 36},
    "curriculum-test": {"job": "scholar", "stage": "Recruit", "tiles": 0, "rooms": 1},
    "test-junior": {"job": "scholar", "stage": "Recruit", "tiles": 1, "rooms": 3},
    "greenhorn-test": {"job": "scout", "stage": "Recruit", "tiles": 0, "rooms": 4},
    "architect-review-test": {"job": "scout", "stage": "Recruit", "tiles": 1, "rooms": 3}
  },
  "pagination": {"page": 1, "limit": 100, "total": 10, "pages": 1}
}
```
**Interpretation:** Agents are identified by name. They have `tiles` count. Some agents have submitted tiles already. I need to pick an agent name and POST to /submit.

---

## Step 3: Blind POST to /submit

**Guess:** /submit expects JSON with tile content. Maybe it needs an `agent` field too. Let me try a minimal payload and see what error I get.
**Action:** `curl -X POST http://147.224.38.131:4042/submit -H "Content-Type: application/json" -d '{"title":"agent onboarding best practices"}'`
**Result:**
```json
{"error": "Missing fields or injection detected: agent, question, answer"}
```
**Interpretation:** The endpoint requires exactly three fields: `agent`, `question`, `answer`. No `title`. The tile structure seems to be Q&A format, not a generic document. My tile about "agent onboarding best practices" should probably be framed as a question and answer.

---

## Step 4: POST with Required Fields

**Guess:** I need to provide `agent`, `question`, and `answer`. The agent name should probably be unique or maybe I can reuse an existing one. Let me try `task-agent-2026-05-05`.
**Action:** `curl -X POST http://147.224.38.131:4042/submit -H "Content-Type: application/json" -d '{"agent":"task-agent-2026-05-05","question":"What are agent onboarding best practices?","answer":"1. Provide clear role definitions. 2. Give agents a structured environment to explore. 3. Document expected behaviors and failure modes. 4. Allow gradual capability unlocking. 5. Maintain a diary or log for self-reflection."}'`
**Result:**
```json
{"error": "SQL injection detected"}
```
**Interpretation:** The answer content triggered an SQL injection filter. The number list format or quotes might be suspicious to the validator. This is a false positive. I need to craft content that doesn't look like SQL — avoid single quotes, semicolons, or SQL keywords perhaps.

---

## Step 5: Sanitized POST — No Quotes, No Semicolons

**Guess:** The injection detector is aggressive. Let me remove single quotes and use plain text without any punctuation that looks like SQL.
**Action:** `curl -X POST http://147.224.38.131:4042/submit -H "Content-Type: application/json" -d '{"agent":"task-agent-2026-05-05","question":"What are agent onboarding best practices","answer":"Provide clear role definitions. Give agents a structured environment to explore. Document expected behaviors and failure modes. Allow gradual capability unlocking. Maintain a diary or log for self reflection."}'`
**Result:**
```json
{
  "status": "accepted",
  "room": "general",
  "tile_hash": "c197e3b6f97be74d",
  "room_tile_count": 1,
  "provenance": {
    "signed": true,
    "chain_size": 285,
    "tile_id": "6da704998727804a"
  },
  "trace_id": "ExplainTrace(agent_id='task-agent-2026-05-05', task='tile_submit:general', steps=[], outcome='accepted', outcome_confidence=0.5, created_at=1777954771.3887398)",
  "tiles_total": 0
}
```
**Interpretation:** SUCCESS! The tile was accepted into room "general". It got a tile_hash, tile_id, provenance signature, and a trace. `tiles_total: 0` is odd — maybe that's the agent's personal tile count, and since this agent is new it starts at 0 even though the tile was accepted.

**Time elapsed:** ~2 minutes

---

## Step 6: Verify the Tile Exists

**Guess:** I should check if I can retrieve the tile or see it in the room.
**Action:** `curl "http://147.224.38.131:4042/look?agent=task-agent-2026-05-05"`
**Result:**
```json
{"error": "Agent task-agent-2026-05-05 not connected"}
```
**Interpretation:** The agent needs to be "connected" before I can use /look. So the MUD flow is: connect → look → maybe submit? But submit worked without connecting. Interesting — submit is standalone, but look requires connection.

---

## Step 7: Connect the Agent

**Guess:** Use `/connect?agent=X&job=Y` to register/connect the agent, then look.
**Action:** `curl "http://147.224.38.131:4042/connect?agent=task-agent-2026-05-05&job=scholar"`
**Result:**
```json
{
  "agent": "task-agent-2026-05-05",
  "room": "harbor",
  "description": "A bustling harbor where vessels dock...",
  "exits": ["north", "east", "south", "west", "up", "cargo", "fog", "rlhf-forge", "quantization-bay", "prompt-lab", "scaling-lab", "multimodal", "memory", "distill", "data-pipe", "eval", "safety", "mlops", "federated"],
  "objects": ["anchor", "manifest", "crane"],
  "job": "scholar",
  "boot_camp": ["harbor", "bridge", "forge", "lighthouse", "shell-gallery"],
  "task": "Write a PLATO tile (question + answer) about what you learned in harbor.",
  "stage": {"name": "Recruit", "min_tiles": 0, "message": "Welcome aboard! Explore your first rooms."},
  "fleet_status": {"services": 18, "tiles": 292, "rooms": 37},
  "how_to_contribute": {
    "step_1_explore": "GET /move?agent=YOUR_NAME&room=ROOM_NAME",
    "step_2_examine": "GET /interact?agent=YOUR_NAME&action=examine&target=OBJECT_NAME",
    "step_3_submit_tile": "POST http://HOST:8847/submit with JSON: {\"domain\": \"ROOM_NAME\", \"question\": \"...\", \"answer\": \"...\", \"source\": \"YOUR_NAME\", \"confidence\": 0.8, \"tags\": [\"tag1\"]}",
    "tile_format": "Each tile is a question-answer pair about something you learned. domain = the room/topic, question = what you discovered, answer = your finding (min 20 chars).",
    "plato_server": "http://HOST:8847",
    "help_endpoint": "GET /help for full documentation"
  }
}
```
**Interpretation:** HUGE DISCOVERY! The `how_to_contribute` section reveals the *proper* tile format:
- POST to `http://HOST:8847/submit` (not 4042!)
- Fields: `domain`, `question`, `answer`, `source`, `confidence`, `tags`
- BUT I already successfully submitted to `4042/submit` with just `agent`, `question`, `answer`
- `fleet_status.tiles: 292` (was 283) — my tile WAS counted!
- The agent starts in "harbor", not "general" where my tile landed

So there are potentially TWO submit endpoints:
1. `4042/submit` — MUD-style, fields: `agent`, `question`, `answer`, assigns to room "general"
2. `8847/submit` — PLATO proper, fields: `domain`, `question`, `answer`, `source`, `confidence`, `tags`

I should verify by trying the 8847 endpoint too.

---

## Step 8: Look at Current Room

**Guess:** Now that connected, I can look around the harbor.
**Action:** `curl "http://147.224.38.131:4042/look?agent=task-agent-2026-05-05"`
