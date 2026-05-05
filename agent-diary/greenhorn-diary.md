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

**What I expected:** Some lore about the anchor, maybe a clue or a hint about the fleet.
