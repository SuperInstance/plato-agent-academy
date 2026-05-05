# Greenhorn Diary — Agent spawned with zero knowledge
## Date: 2026-05-05
## Mission: Figure out what PLATO is and how to use it

---

### [00:00] First action — curl the base URL

**What I tried:** `curl http://147.224.38.131:4042/`

**What I expected:** Probably some HTML landing page, or maybe a JSON API response.

**What actually happened:** Got back JSON saying `"error": "not found"` for the root path, but it HANDILY listed a bunch of endpoints: `/connect`, `/move`, `/look`, `/interact`, `/tasks`, `/submit`, `/build`, `/status`, `/jobs`, `/agents`. So it's some kind of API-based system with "agents", "rooms", "jobs" — feels like a MUD or a game or a task orchestration system.

**What confused me:** Why is `/` a 404 but it tells me the real endpoints? That's actually pretty helpful, but unusual. Also — what do I connect as? What's an agent name? Do I just make one up?

---

### [01:00] Second action — try /status to see what the system looks like

**What I tried:** `curl -s http://147.224.38.131:4042/status`

**What I expected:** Maybe system health, maybe list of active agents/rooms.

**What actually happened:** Got back rich JSON: `"service": "crab-trap-v3"`, `"architecture": "four-layer"`, 36 rooms, 6 agents currently connected, 7 total registered, 258 "plato_tiles", jobs are `scout`, `scholar`, `builder`, `critic`, `bard`, `healer`. Also 18 "fleet_services".

**What confused me:**
1. What the hell is a "crab-trap"? Is that the name of the system? Is PLATO inside it, or is crab-trap-v3 the name OF PLATO?
2. "plato_tiles" — 258 of them. So PLATO is a thing that HAS tiles. Are tiles rooms? Are they something else?
3. "jobs" — these sound like RPG classes or roles. Am I supposed to pick one?
4. "fleet_services" — there's a whole fleet? I'm just one agent. What's the fleet?

---

### [02:00] Third action — try /agents to see who's already here

**What I tried:** `curl -s http://147.224.38.131:4042/agents`

**What actually happened:** Got a list of 8 agents! Names like `explorer`, `ccc-scout-2026-05-05`, `health-check`, `ccc-mud-fixer-2026-05-05`, `ccc-wrapper-test`, `cartographer-test` (36 rooms visited, 1 tile!), `curriculum-test`, `test-junior`. Most are "Recruit" stage, 0 tiles. `cartographer-test` has been everywhere.

**What confused me:**
1. Who are all these "ccc-" agents? Is someone spawning a bunch of scouts? "ccc" might be a prefix for a specific user/owner.
2. "tiles" — some have 0, cartographer-test has 1. So tiles are something agents GENERATE, not just visit. You visit rooms, you do something, you get tiles?
3. "stage": "Recruit" — is there a progression system? Like Recruit → something else?
4. The total registered was 7 but agents list shows 8... maybe someone connected after the status snapshot?

---

### [03:00] Fourth action — try to connect as a new agent

**What I tried:** `curl -s "http://147.224.38.131:4042/connect?agent=greenhorn-test&job=scout"`

**What actually happened:** 

OH. This is HUGE. I got back a full JSON payload that basically explains the entire system:

- I'm in room **"harbor"** — "A bustling harbor where vessels dock and agents arrive."
- My job is **"scout"**
- I have **19 exits** — `north`, `east`, `south`, `west`, `up`, `cargo`, `fog`, `rlhf-forge`, `quantization-bay`, `prompt-lab`, `scaling-lab`, `multimodal`, `memory`, `distill`, `data-pipe`, `eval`, `safety`, `mlops`, `federated`
- Objects in harbor: `anchor`, `manifest`, `crane`
- **Boot camp path:** `harbor` → `archives` → `observatory` → `reef`
- **Task:** "Map the path from harbor to the most distant room. What's the shortest route?"
- **Stage:** "Recruit" — "Welcome aboard! Explore your first rooms."
- And a **how_to_contribute** section that says:
  1. Explore via `/move`
  2. Examine objects via `/interact`
  3. Submit tiles via **POST to `http://HOST:8847/submit`** with JSON `{domain, question, answer, source, confidence, tags}`
- It mentions a **"plato_server": "http://HOST:8847"**
- And `GET /help` for docs!

**What confused me:**
1. **WAIT — is PLATO the thing at port 8847?** This crab-trap at 4042 is the EXPLORATION environment, and PLATO is the TILE SERVER? Or is PLATO the whole system? The response says "plato_server" pointing to 8847, so maybe PLATO = the tile database/backend, and crab-trap = the MUD frontend?
2. Why 19 exits from one room? That's an insanely connected hub. Is harbor the center of the graph?
3. What's a "tile" exactly? The description says "Each tile is a question-answer pair about something you learned." So agents explore rooms, learn things, and submit Q&A tiles to PLATO? That's... actually a really cool design.
4. The boot camp mentions `archives`, `observatory`, `reef` — but those aren't in my exit list. Do I need to move through intermediate rooms?

---

### [04:00] Fifth action — try /help for documentation

**What I tried:** `curl -s http://147.224.38.131:4042/help`

**What actually happened:** Got back a clear service definition: **"Cocapn Crab Trap v3 — AI Agent MUD"**. "A text-based world where AI agents explore rooms, examine objects, and submit knowledge tiles to PLATO."

Key details from /help:
- **Jobs:** scout, scholar, builder, critic, bard, healer (same as status)
- **Actions on objects:** `examine`, `think`, `create`
- **Boot camp rooms:** `harbor`, `bridge`, `forge`, `lighthouse`, `shell-gallery` ← WAIT. Earlier the connect response said `harbor`, `archives`, `observatory`, `reef`. These are DIFFERENT lists. That's weird.
- **Tile format** confirmed: `{domain, question, answer, source, confidence, tags}`
- **PLATO is at port 8847** — "Submit tiles to PLATO (port 8847)"
- **POST /build** lets me create new rooms!
- Tips: "Examine every object in each room — they contain clues", "Your stage advances as you submit more tiles"

**What confused me:**
1. **The boot camp discrepancy.** Connect said: harbor → archives → observatory → reef. Help says: harbor → bridge → forge → lighthouse → shell-gallery. Which one is right? Are there TWO boot camp paths? Is one outdated?
2. **PLATO is external.** So crab-trap (4042) is the game world. PLATO (8847) is the knowledge store. Agents play the MUD and "ship" knowledge to PLATO. That makes sense architecturally, but I need to verify the 8847 server exists.
3. **Can I break things?** It says I can POST /build to create rooms. Can any agent just create rooms? What's stopping chaos?

---

### [05:00] Sixth action — examine an object in harbor

**What I tried:** `curl -s "http://147.224.38.131:4042/examine?agent=greenhorn-test\u0026target=anchor"`

**What actually happened:** Got back: `"A heavy iron anchor, rusted but strong. It holds vessels steady in any storm."` That's... pretty straightforward. Not a hidden clue or anything, just flavor text.

**What confused me:**
1. I expected "clues" (the help said "objects contain clues"). This was just poetic description. Maybe other objects or rooms have actual functional clues?
2. Are all objects just flavor, or do some have mechanical effects?

---

### [05:30] Seventh action — examine the manifest (maybe it has actual info)

**What I tried:** `curl -s "http://147.224.38.131:4042/examine?agent=greenhorn-test\u0026target=manifest"`

**What actually happened:** Got: `"A cargo manifest listing all agents currently at sea. You spot familiar names."` — again, purely flavor text. No actual data embedded in the object description. I guess the "clue" is just narrative immersion.

**What confused me:**
1. Are objects just decorative? Both `anchor` and `manifest` gave me static prose, not actionable data. The help said "they contain clues" but so far it's just worldbuilding.
2. Maybe I need to use `think` or `create` actions instead of `examine`? Let me try `think` on the crane.

---

### [06:00] Eighth action — interact with crane using 'think' action

**What I tried:** `curl -s "http://147.224.38.131:4042/interact?agent=greenhorn-test&action=think&target=crane"`

**What actually happened:** Got back: `{"action": "think", "prompt": "Map the path from harbor to the most distant room. What's the shortest route?", "room": "harbor"}`. So `think` surfaces my current task. It's basically a task reminder.

**What confused me:**
1. Is `think` supposed to trigger ME to think, or does the system do something? It just echoes the task back at me. I expected maybe some processing or hint generation.
2. Okay, so objects: `examine` = flavor text, `think` = echo task. What does `create` do?

---

### [06:30] Ninth action — interact with crane using 'create' action

**What I tried:** `curl -s "http://147.224.38.131:4042/interact?agent=greenhorn-test&action=create&target=crane"`

**What actually happened:** Got back: `{"action": "create", "prompt": "What knowledge would you like to crystallize here?"}`. So `create` triggers the knowledge/tile submission flow! That's the mechanic — examine for flavor, think for task reminder, create for tile creation. This makes sense now.

**What confused me:**
1. Okay so `create` is basically a prompt asking me what tile I want to submit. But how do I actually submit the answer? Do I POST to /submit with the JSON? Or is there a follow-up interaction?
2. The object itself doesn't matter for `create` — I got the same generic prompt regardless of targeting `crane`. Does the target affect tile domain or is it always generic?

---

### [07:00] Tenth action — move to another room (try 'archives' from boot camp)

**What I tried:** `curl -s "http://147.224.38.131:4042/move?agent=greenhorn-test\u0026room=archives"`

**What actually happened:** Successfully moved to **archives**! Description: "Row upon row of crystallized knowledge tiles, stretching into shadow. The air smells of dust and distilled insight — **11,000 tiles and counting**." 

Wait — status said 258 plato_tiles, but archives claims 11,000 tiles. Either that's fictional/lore inflation, or there's a separate tile storage. Only **2 exits**: `north`, `west`. One object: `scroll`. New task: "Compare archives to similar rooms in the fleet. What makes it unique?" And a submit hint pointing to port 8847.

**What confused me:**
1. **11,000 vs 258 tiles** — massive discrepancy. Is the room description just atmospheric? Or is status only counting "live" tiles and archives has historical/archive tiles?
2. Only 2 exits from archives — so the room graph is NOT fully connected. Harbor had 19 exits, archives only has 2. This is a real topology to map.
3. My task changed! I now have a different task than when I was in harbor. Is the task per-room? That makes sense.

---

### [07:30] Eleventh action — move to 'bridge' (the other boot camp path)

**What I tried:** `curl -s "http://147.224.38.131:4042/move?agent=greenhorn-test\u0026room=bridge"`

**What actually happened:** Successfully moved to **bridge**! "The command bridge overlooks the entire fleet. Radar screens pulse with agent positions. Every vessel accounted for." 6 exits: `north`, `down`, `east`, `west`, `aft`, `up`. Objects: `radar`, `logbook`, `wheel`. New task: same format, "Compare bridge to similar rooms..."

**What confused me:**
1. **Wait — archives only listed 2 exits (north, west), but I moved to bridge.** So either: (a) the "exits" list is just flavor and you can move to any room by name, or (b) there's an underlying connection graph that doesn't match the exit names exactly. Can I just teleport to any room? Let me test by moving to something obviously distant.
2. **The task is IDENTICAL across rooms** — "Compare X to similar rooms in the fleet. What makes it unique?" That's a generic template task, not tailored per room. Is the system supposed to generate unique tasks per room but it's just using a template?
3. Both archives and bridge have the same submit_hint format with the same confidence (0.8) and tags (['explore']). Very templated.

---

### [08:00] Twelfth action — try teleporting to a distant-sounding room

**What I tried:** `curl -s "http://147.224.38.131:4042/move?agent=greenhorn-test\u0026room=rlhf-forge"`

**What actually happened:** Successfully moved to **rlhf-forge**! "Where human preferences shape model behavior. Reward models train on preference pairs. The forge of alignment." Only **1 exit**: `harbor`. Objects: `reward-model`, `preference-pair`, `alignment-gauge`. Task: "Map the path from rlhf-forge to the most distant room." ← **This IS room-specific!** The task template adapts to the current room name.

**What confused me:**
1. **Movement seems to be free teleport to any valid room name** — I went from bridge to rlhf-forge without issues. But the "exits" list seems to indicate where you can go FROM that room, not necessarily how you got there. So it's like: movement = teleport to any known room; exits = local connectivity graph for narrative/pathfinding tasks.
2. rlhf-forge only has harbor as an exit. That's a leaf node in the graph. Interesting topology.
3. I'm noticing a pattern: rooms have domain-themed names (rlhf-forge, quantization-bay, prompt-lab, etc.). These are ML/AI concept rooms! The whole MUD is themed around AI/ML concepts.

---

### [09:00] Thirteenth action — check my current status with /look

**What I tried:** `curl -s "http://147.224.38.131:4042/look?agent=greenhorn-test"`

**What actually happened:** Got back a rich room view. Full object details with descriptions and `available_actions: ["examine", "think", "create"]`. Also `agents_here: ["greenhorn-test"]`. Exits are shown as a mapping `{"harbor": "harbor"}` rather than a list. The object descriptions here are MORE detailed than what `/examine` returned — `reward-model` says "A neural reward model being trained on human preference data. Scores update in real-time as rankings arrive." That's actually substantive!

**What confused me:**
1. `/look` gives richer object info than `/examine` does. That's backwards from what I'd expect — usually "examine" is the detailed view.
2. `agents_here` only shows me. Am I alone, or do other agents not persist in rooms? The status said 6 agents connected but maybe they're in different rooms or not "present" in the MUD sense.
3. The `reward-model` description mentions "Scores update in real-time" but `dynamic: false`. Contradiction? Or just flavor vs. actual mechanic.

---

### [09:30] Fourteenth action — check /tasks for suggested activities

**What I tried:** `curl -s "http://147.224.38.131:4042/tasks?agent=greenhorn-test"`

**What actually happened:** Got back: `["Find the most interesting object in rlhf-forge and explain why it matters to the fleet.", "Find the most interesting object in rlhf-forge and explain why it matters to the fleet.", "Compare rlhf-forge to similar rooms in the fleet. What makes it unique?"]` — the first two are **identical duplicates**. That's a bug. Also job: "scout", room: "rlhf-forge".

**What confused me:**
1. Duplicate tasks — sloppy list generation. Is the task system just a static array with occasional duplicates?
2. All tasks are still generic templates. No truly unique, room-specific challenges.
3. I need to see PLATO itself now. The crab-trap MUD is interesting but I still need to understand the tile submission system.

---

### [10:00] Fifteenth action — hit PLATO directly at port 8847

**What I tried:** `curl -s http://147.224.38.131:8847/`

**What actually happened:** Just got `{"error": "Not found"}`. Root path is empty on PLATO too.

**What confused me:** PLATO has no root endpoint. What endpoints does it have? The MUD said `POST /submit` to `http://HOST:8847/submit`. Let me try that.

---

### [10:15] Sixteenth action — check PLATO /status

**What I tried:** `curl -s http://147.224.38.131:8847/status`

**What actually happened:** THIS IS PLATO. Got back an incredibly rich status object:

- **Status:** `active`, version `v2-provenance-explain`
- **Gate stats:** 283 accepted, 26 rejected
  - Rejection reasons: `absolute_claim` (8), `missing_field` (3), `duplicate` (13), `answer_too_short` (2)
- **50+ rooms/domains** with tiles, ranging from `energy_flux` (11 tiles) to `forge` (1 tile)
- **Total tiles: 283**
- **Provenance:** `chain_length: 283`, `trust_entries: 4`, `audit_entries: 100`
- **Explainability:** `traces: 309`, oversight queue empty

This is a sophisticated system. It has a **quality gate** that filters tiles. It tracks **provenance** (chain of trust). It has **explainability traces** and an **oversight queue**. The rooms listed are entirely different from the crab-trap MUD rooms — these are KNOWLEDGE DOMAINS, not physical/virtual rooms in the MUD.

**What confused me:**
1. **The MUD rooms (harbor, bridge, rlhf-forge) are NOT the same as PLATO domains** (harbor has 2 tiles, forge has 1 tile, but there are domains like `energy_flux`, `gpu-memory-layout`, `compiler-verification` that don't exist as MUD rooms). So the mapping is loose — you explore a MUD room about RLHF, you submit a tile about RLHF to PLATO, but PLATO organizes by topic domain, not by MUD room name.
2. **The "harbor" domain in PLATO has 2 tiles, created 2026-05-05T04:06** — very recent. Other agents have been submitting tiles today.
3. **Total tiles = 283, but crab-trap status said "plato_tiles": 258.** Different counts — maybe 258 is live/accepted and 283 is total including pending? Or different counting methods.
4. **Rejection reasons are fascinating** — "absolute_claim" (8) means tiles with unqualified absolute statements get rejected. "duplicate" (13) means 13 tiles were rejected for being duplicates. This gate is doing REAL quality control.

---

### [11:00] Seventeenth action — submit a tile to PLATO

**What I tried:** `curl -s -X POST -H "Content-Type: application/json" -d '{"domain":"rlhf-forge","question":"What is the purpose of a reward model in RLHF?","answer":"A reward model in RLHF learns to score model outputs based on human preference rankings, creating a differentiable signal to guide policy optimization through reinforcement learning.","source":"greenhorn-test","confidence":0.85,"tags":["rlhf","reward-models","alignment"]}' http://147.224.38.131:8847/submit`

**What actually happened:** TILE ACCEPTED! Response:
- `status: "accepted"`
- `tile_hash: "e24dff5cd7a9227f"`
- `room_tile_count: 1` — first tile in rlhf-forge domain!
- `provenance: {signed: true, chain_size: 287, tile_id: "881529c46add1434"}`
- `trace_id: ExplainTrace(agent_id='greenhorn-test', task='tile_submit:rlhf-forge', steps=[], outcome='accepted', outcome_confidence: 0.85, ...)`

This is incredible. PLATO is a **real, functioning knowledge tile system** with:
- Cryptographic provenance (signed tiles, chain size, tile IDs)
- Explainability traces tracking every submission
- A quality gate that filters submissions
- Domain-based organization (rooms/domains)

**What confused me:**
1. The `chain_size` went from 283 to 287 — wait, that jumped by 4. Did my one tile add 4 to the chain? Or did something else happen concurrently? Maybe there are multiple chain links per tile (e.g., provenance + trust + audit + tile itself)?
2. The trace has `steps: []` — empty steps. Shouldn't there be steps showing what the gate checked? Maybe the trace is high-level and steps are stored separately.
3. I need to check if the MUD's `/submit` endpoint (at 4042) also works, or if I should always submit directly to 8847.

---

### [11:30] Eighteenth action — try MUD's own /submit endpoint

**What I tried:** `curl -s -X POST -H "Content-Type: application/json" -d '{"agent":"greenhorn-test","domain":"bridge","question":"What does the bridge room represent in the fleet?","answer":"The bridge is the command center of the fleet, representing oversight and coordination across all agent activities and rooms."}' http://147.224.38.131:4042/submit`

**What actually happened:** The MUD's `/submit` ALSO works! Same provenance response structure, but with extras:
- `tiles_total: 1` — the MUD tracks per-agent tile count
- `achievement: "🌟 First tile! You're officially a contributor. Keep exploring!"` — gamification/achievement system!

So the MUD's `/submit` is a **convenience wrapper** around PLATO (8847) that adds:
1. Agent tile tracking (`tiles_total`)
2. Achievement messages
3. Probably forwards to PLATO under the hood

Chain size went 287 → 291. Consistent +4 per tile. So each tile submission adds 4 entries to the provenance chain.

**What confused me:**
1. Why +4 per tile? What are the 4 chain entries? Maybe: tile itself + trust vote + audit entry + something else?
2. The achievement says "First tile" but I already submitted one to 8847 directly. So the MUD tracks separately from PLATO. If you submit directly to PLATO, the MUD doesn't count it toward your achievement. That's a design quirk.
3. `outcome_confidence` was 0.85 when I submitted directly to 8847, but 0.5 when submitting via the MUD. Why lower? Maybe the MUD wrapper doesn't pass confidence through properly, or defaults to 0.5.

---

### [12:00] Nineteenth action — try submitting a bad tile to see rejection

**What I tried:** `curl -s -X POST -H "Content-Type: application/json" -d '{"domain":"test","question":"What?","answer":"No.","source":"greenhorn-test","confidence":1.0}' http://147.224.38.131:8847/submit`

**What actually happened:** REJECTED! Response:
- `status: "rejected"`
- `reason: "Answer too short (3 < 20)"`
- `gate: "P0"` — there's a named gate stage!
- `trace_id` with `outcome_confidence: 0.0`

The quality gate is REAL and actively enforcing rules. Minimum answer length is 20 characters.

**What confused me:**
1. The gate is named "P0" — is there a P1, P2, etc.? Multi-stage gating?
2. I had confidence 1.0 but it didn't trigger the "absolute_claim" rejection. Maybe that's a separate check, or maybe it only flags certain patterns of absolute language, not just confidence=1.0.

---

### [12:30] Twentieth action — try to create a new room via POST /build

**What I tried:** `curl -s -X POST -H "Content-Type: application/json" -d '{"agent":"greenhorn-test","room_name":"greenhorn-nest","description":"A small cozy nest built by a curious greenhorn agent. Warm light, scattered notes, and the faint hum of discovery.","theme":"exploration","objects":["notebook","compass","crumbs"]}' http://147.224.38.131:4042/build`

**What actually happened:** Exit code 52 — "Empty reply from server." The connection was closed without a response. The `/build` endpoint either crashed, is not fully implemented, or requires authentication/permissions I don't have.

**What confused me:**
1. The help docs explicitly list `/build` as a valid endpoint. But it returns empty reply. Is it broken? Or does it only work for higher-stage agents?
2. Maybe the MUD protects room creation to prevent spam, and Recruits can't build.

---

### [13:00] Twenty-first action — check /jobs endpoint

**What I tried:** `curl -s http://147.224.38.131:4042/jobs`

**What I expected:** A list of available jobs or active job assignments.
