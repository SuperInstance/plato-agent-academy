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
