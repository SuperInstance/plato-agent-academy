# Junior Developer Diary — PLATO Room Creation
**Started:** 2026-05-05 12:08 GMT+8  
**Mission:** Create a 'tide-pool' themed research lab room with at least 2 objects at http://147.224.38.131:4042/
**Constraint:** No fleet docs, just pure API exploration

---

## Attempt 1 — Root GET

**Endpoint:** `GET http://147.224.38.131:4042/`
**What I sent:** Just a basic curl GET
**What came back:** 
```json
{"error": "not found", "path": "/", "endpoints": ["/connect?agent=X&job=Y", "/move?agent=X&room=Y", "/look?agent=X", "/interact?agent=X&action=Y&target=Z", "/tasks?agent=X", "/submit (POST)", "/submit/result (POST)", "/build (POST)", "/status", "/jobs", "/agents"]}
```
**Analysis:** This looks like a MUD/game system. `/build (POST)` is the obvious candidate for creating a room. But I need to connect first? The `/connect?agent=X&job=Y` endpoint suggests I need an agent name. Let me try connecting first, then explore build.

---

## Attempt 2 — Connect as an agent

**Endpoint:** `GET http://147.224.38.131:4042/connect?agent=test-junior&job=room-builder`
**What I sent:** curl with agent and job params
**What came back:** TBD

