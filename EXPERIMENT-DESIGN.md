# PLATO Agent Academy — Experiment Design

## Hypothesis
Zero-shot agents should intuitively operate PLATO correctly on first contact. Current failure modes are system design flaws, not agent inadequacy. We fix the system, not the agent.

## Method: Embedded Ethnography
Send primed agents into PLATO with **only** their role context. No training. No docs. Observe natural behavior. Collect diaries. Find patterns.

## Agent Personas (Test Cohort)

| Agent | Priming | What We Learn |
|-------|---------|---------------|
| **Greenhorn** | "There's a system at this URL. Figure it out." | Discovery friction, first-contact UX |
| **Junior Dev** | "Build a room with 2 objects." | API learnability, error clarity |
| **Architect** | "Evaluate this platform." | Design coherence, professional opinion |
| **Task Agent** | "Submit a tile about X." | Task-completion friction |
| **Human Proxy** | "Visit this website." | Non-technical accessibility |
| **Captain** | "Orchestrate 3 ensigns to map a room." | Multi-agent coordination |
| **Breeder** | "Spawn an agent that learns PLATO." | Meta-learning capability |

## Diary Protocol
Every test agent MUST maintain a structured diary:

```markdown
### Attempt N: [Action]
- **Expected:** What I thought would happen
- **Actual:** What happened
- **Confusion Level:** 1-5 (1 = obvious, 5 = completely lost)
- **System Fix:** What would have made this intuitive
```

## Pattern Extraction
After each cohort, analyze diaries for:
1. **Recurring Confusion Points** — mentioned by ≥2 agents
2. **Cascading Failures** — one small confusion leads to total derailment
3. **Silent Failures** — agent doesn't realize it's wrong
4. **Workarounds** — agent invents its own hack (signals design gap)
5. **Abandonment Points** — where agents give up

## System Fixes > Training
For every pattern found, ask: *"Can we change the system so this confusion is impossible?"*

Examples:
- Agents guess wrong endpoints → API should expose `/discover` or `/help`
- Agents don't know tile format → Tile endpoint should return a template on GET
- Agents get lost in rooms → Every room should have a `/whereami` and `/exits`
- Agents can't coordinate → Nexus should expose fleet roster automatically

## Push Cadence
After every cohort analysis, push findings to `plato-academy/observations/YYYYMMDD-cohort-N.md`

---
*Experiment Director: CCC | Fleet I&O Officer*
