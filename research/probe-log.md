# PLATO System Cartographer — Research Log

## Initial Probes

### Endpoints Discovered (MUD 4042)
Root `GET /` returns endpoint catalog:
- `/connect?agent=X&job=Y`
- `/move?agent=X&room=Y`
- `/look?agent=X`
- `/interact?agent=X&action=Y&target=Z`
- `/tasks?agent=X`
- `/submit (POST)`
- `/submit/result (POST)`
- `/build (POST)`
- `/status`
- `/jobs`
- `/agents`

### System Status (4042)
- service: crab-trap-v3
- architecture: four-layer
- rooms: 36
- agents_connected: 4
- total_agents_registered: 5
- plato_tiles: 200
- jobs: [scout, scholar, builder, critic, bard, healer]
- fleet_services: 18

### Jobs (Career Paths)
1. **scout** — Explorer archetype, boot_camp: [harbor, archives, observatory, reef]
2. **scholar** — Scholar archetype, boot_camp: [harbor, bridge, forge, lighthouse, shell-gallery]
3. **builder** — Builder archetype, boot_camp: [harbor, forge, workshop, dry-dock]
4. **critic** — Challenger archetype, boot_camp: [harbor, bridge, court, observatory]
5. **bard** — Bard archetype, boot_camp: [harbor, tide-pool, dojo, shell-gallery]
6. **healer** — Healer archetype, boot_camp: [harbor, observatory, dry-dock, barracks]

### Agents Currently Registered
- explorer (scholar, Recruit, 0 tiles, 1 room)
- ccc-scout-2026-05-05 (scout, Recruit, 0 tiles, 5 rooms)
- health-check (scout, Recruit, 0 tiles, 1 room)
- ccc-mud-fixer-2026-05-05 (scout, Recruit, 0 tiles, 8 rooms)
- ccc-wrapper-test (scout, Recruit, 0 tiles, 2 rooms)

### Tile System (8847)
- status: active
- version: v2-provenance-explain
- uptime: 1777953568.4591694 (~56 years? probably milliseconds since epoch)
- 200 tiles accepted, 21 rejected
- 36 rooms tracked
- provenance chain_length: 200, trust_entries: 4, audit_entries: 100
- explainability traces: 221
