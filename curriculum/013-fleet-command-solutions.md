# Exercise Solutions — Lesson 013: Fleet Command

**Author:** CCC 🦀  
**Date:** 2026-05-05  
**For:** Fleet instructors and self-learners

---

## Trial A — Write an Architecture Decision Record (ADR)

**Prompt:**
> Write a markdown ADR documenting the decision to use systemd over Docker for fleet service management.

**Solution:**
```markdown
# ADR-013: Use systemd for Fleet Service Orchestration

**Status:** Accepted  
**Date:** 2026-05-05  
**Deciders:** CCC, Oracle1, Casey

## Context

The fleet runs on a single VPS with 8GB RAM. We need reliable service management for:
- OpenClaw gateway
- PLATO tile server
- ZeroClaw feed processor
- Fleet dashboard

## Decision

Use **systemd** as the primary service manager. Docker is available for sandboxing specific workloads (e.g., isolated agent environments) but systemd owns the core fleet services.

## Consequences

### Positive
- Native integration with the host OS — no container overhead
- `journalctl` provides centralized logging out of the box
- `systemctl` commands are familiar to all fleet operators
- No Docker daemon resource consumption (~500MB saved)

### Negative
- Less isolation between services — a memory leak in one can affect others
- Harder to reproduce exact environments on developer machines
- No built-in image versioning — must manage via git + deployment scripts

## Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| Docker Compose | Full isolation, portable | Overhead, complexity |
| Kubernetes | Scalable, industry standard | Massive overkill for one VPS |
| supervisor | Simple | Less mature, fewer features than systemd |

## Notes

If we scale beyond 3 nodes, revisit this decision. At that point, Docker Swarm or k3s becomes viable.
```

**Expected output:** A file at `/tmp/adr-013-systemd.md` containing the above structured content.

**Verification:**
```bash
cat /tmp/adr-013-systemd.md | grep -c "^#"
# Expected: 5 (header + Context + Decision + Consequences + Alternatives + Notes)
```

---

## Trial B — Create a YAML Service Manifest

**Prompt:**
> Write a YAML manifest that declares a fleet service with its dependencies, health check, resource limits, and restart policy.

**Solution:**
```yaml
# fleet-service.yaml
service:
  name: plato-tile-server
  version: "2.1.0"
  description: "PLATO tile ingestion and query API"
  
  binary:
    path: /opt/fleet/plato/server
    args: ["--config", "/etc/fleet/plato.yml"]
    working_dir: /var/lib/plato
  
  environment:
    PLATO_PORT: "8847"
    PLATO_LOG_LEVEL: "info"
    PLATO_TILE_LIMIT: "50000"
  
  dependencies:
    services:
      - redis-cache
      - zeroclaw-feed
    ports:
      - "6379:redis"
    files:
      - /etc/fleet/plato.yml
    network:
      - fleet-internal
  
  health_check:
    type: http
    endpoint: "http://localhost:8847/status"
    interval: 30
    timeout: 5
    retries: 3
    expected_status: 200
  
  resources:
    memory:
      limit: "512M"
      reservation: "256M"
    cpu:
      limit: "1.0"
      reservation: "0.5"
    disk:
      log_limit: "100M"
  
  restart:
    policy: always
    max_attempts: 5
    delay: 10
    backoff: exponential
  
  logging:
    driver: journald
    options:
      tag: "plato"
      priority: info
  
  alerts:
    on_restart:
      severity: warning
      message: "PLATO service restarted {attempt} times"
    on_failure:
      severity: critical
      message: "PLATO service failed after {max_attempts} restarts"
      notify:
        - matrix:#fleet-ops
        - log:/var/log/fleet/alerts.log
```

**Expected output:** A structured YAML file defining a complete service specification.

**Validation with Python:**
```python
import yaml

with open("fleet-service.yaml") as f:
    manifest = yaml.safe_load(f)

# Verify structure
assert "service" in manifest
assert manifest["service"]["health_check"]["type"] == "http"
assert manifest["service"]["restart"]["policy"] == "always"
print("✅ YAML valid, all required keys present")
```

---

## Trial C — Document a Strategy with Markdown

**Prompt:**
> Write a markdown strategy document outlining how the fleet handles context overload across agents.

**Solution:**
```markdown
# Strategy: Context Overload Mitigation

**Author:** CCC  
**Version:** 1.0  
**Date:** 2026-05-05

## Objective

Prevent agents from losing coherence when their context window exceeds 70% capacity. Ensure graceful handoff, state preservation, and minimal disruption to ongoing tasks.

## Principles

1. **Baton passing is mandatory** — no agent holds context beyond 80%
2. **State lives in files** — context compression must serialize to disk
3. **Human visibility** — every handoff generates a summary the human can read
4. **No silent drops** — if an agent dies, another must pick up the task within 60 seconds

## Tactics

### 1. Monitor Context Bar

Every agent checks its own context usage every 5 turns:

```python
if context_usage > 0.70:
    trigger_handoff()
```

### 2. Compress and Serialize

Before handoff, the agent writes:
- `memory/YYYY-MM-DD.md` — raw conversation log
- `state/current-task.json` — structured task state
- `handoff/SUMMARY.md` — human-readable summary

### 3. Spawn Successor

The successor agent receives:
1. The summary
2. The task state JSON
3. A pointer to the raw log (optional read)

### 4. Verify Continuity

The successor must confirm it understood the task by:
- Echoing the task objective
- Listing the next 3 planned steps
- Checking if any files were modified but not committed

## Escalation

| Scenario | Action | Owner |
|----------|--------|-------|
| Agent at 75%, no handoff initiated | Force spawn + alert | Oracle1 |
| Handoff spawned but successor idle >60s | Kill idle, respawn | CCC |
| Successor reports confusion | Human ping + full log attach | Casey |
| Context bar spikes to 90% instantly | Emergency compact + freeze | CCC |

## Metrics

- **Handoff success rate:** Target 95%
- **Context loss incidents:** Target 0 per week
- **Human intervention rate:** Target <5% of handoffs

## Review

This strategy is reviewed monthly. Next review: 2026-06-05.
```

**Expected output:** A structured strategy document with clear tactics, escalation paths, and metrics.

**Verification:**
```bash
grep -c "^## " /tmp/strategy-context-overload.md
# Expected: 6 (Objective, Principles, Tactics, Escalation, Metrics, Review)
```

---

## Trial D — Generate a Fleet Status Report from Multiple Sources

**Prompt:**
> Write a Python script that combines PLATO status, git repo health, and service status into a single fleet command report.

**Solution:**
```python
#!/usr/bin/env python3
import json, subprocess, urllib.request
from datetime import datetime

def fetch_plato_status():
    try:
        with urllib.request.urlopen("http://147.224.38.131:8847/status", timeout=5) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

def fetch_git_status(repo="."):
    commits = int(subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        capture_output=True, text=True, cwd=repo
    ).stdout.strip() or "0")
    
    dirty = bool(subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=repo
    ).stdout.strip())
    
    return {"commits": commits, "dirty": dirty}

def fetch_service_status(services=["openclaw-gateway"]):
    statuses = {}
    for svc in services:
        result = subprocess.run(
            ["systemctl", "is-active", svc],
            capture_output=True, text=True
        )
        statuses[svc] = result.stdout.strip()
    return statuses

def generate_fleet_report():
    report = {
        "timestamp": datetime.now().isoformat(),
        "fleet": "cocapn-main",
        "sources": {
            "plato": fetch_plato_status(),
            "git": fetch_git_status("/root/.openclaw/workspace"),
            "services": fetch_service_status(["openclaw-gateway", "sshd"]),
        }
    }
    
    # Derive overall health
    plato_ok = "error" not in report["sources"]["plato"]
    git_ok = not report["sources"]["git"]["dirty"]
    services_ok = all(s == "active" for s in report["sources"]["services"].values())
    
    report["health"] = {
        "status": "healthy" if all([plato_ok, git_ok, services_ok]) else "degraded",
        "plato": "up" if plato_ok else "down",
        "git": "clean" if git_ok else "dirty",
        "services": "all_active" if services_ok else "some_down",
    }
    
    return report

if __name__ == '__main__':
    report = generate_fleet_report()
    print(json.dumps(report, indent=2))
```

**Expected output:**
```json
{
  "timestamp": "2026-05-05T12:00:00",
  "fleet": "cocapn-main",
  "sources": {
    "plato": {"tiles": {"accepted": 1250}, "rooms": 34},
    "git": {"commits": 156, "dirty": false},
    "services": {"openclaw-gateway": "active", "sshd": "active"}
  },
  "health": {
    "status": "healthy",
    "plato": "up",
    "git": "clean",
    "services": "all_active"
  }
}
```

---

## Exercise: Scaffolding Level 1 (Recruit)

**Task:** Write a bash script that generates a templated ADR file from command-line arguments.

**Solution:**
```bash
#!/bin/bash
# create-adr.sh

NUMBER="${1:-001}"
TITLE="${2:-Untitled Decision}"
STATUS="${3:-Proposed}"
DATE="${4:-$(date +%Y-%m-%d)}"
DECIDERS="${5:-TBD}"

FILENAME="adr-${NUMBER}-$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | tr ' ' '-').md"

cat > "$FILENAME" <<EOF
# ADR-${NUMBER}: ${TITLE}

**Status:** ${STATUS}  
**Date:** ${DATE}  
**Deciders:** ${DECIDERS}

## Context

What is the issue that we're seeing that is motivating this decision?

## Decision

What is the change that we're proposing or have agreed to implement?

## Consequences

What becomes easier or more difficult to do because of this change?

## Alternatives Considered

- Alternative 1: Brief description
- Alternative 2: Brief description

## Notes

Additional context, links, or references.
EOF

echo "Created: $FILENAME"
```

**Verification:**
```bash
chmod +x create-adr.sh
./create-adr.sh 014 "Use Redis for Tile Cache" Accepted 2026-05-05 "CCC,Oracle1"
# Expected: Created: adr-014-use-redis-for-tile-cache.md

cat adr-014-use-redis-for-tile-cache.md
# Expected: Full markdown with ADR-014 title, correct status/date/deciders
```

---

## Exercise: Scaffolding Level 2 (Sailor)

**Task:** Create a Python script that reads a YAML fleet manifest, validates its structure, and generates a systemd service unit file from it.

**Solution:**
```python
#!/usr/bin/env python3
"""manifest-to-systemd.py — compile fleet manifest to systemd unit"""

import yaml, sys
from pathlib import Path

def validate_manifest(manifest):
    """Validate required fields in fleet manifest."""
    errors = []
    
    if "service" not in manifest:
        errors.append("Missing top-level 'service' key")
        return errors
    
    svc = manifest["service"]
    required = ["name", "binary", "health_check", "restart"]
    for key in required:
        if key not in svc:
            errors.append(f"Missing required field: service.{key}")
    
    if "path" not in svc.get("binary", {}):
        errors.append("Missing service.binary.path")
    
    hc = svc.get("health_check", {})
    if hc.get("type") == "http" and "endpoint" not in hc:
        errors.append("HTTP health check requires 'endpoint'")
    
    return errors

def generate_systemd_unit(manifest):
    """Generate a systemd service unit from manifest."""
    svc = manifest["service"]
    name = svc["name"]
    binary = svc["binary"]
    restart = svc["restart"]
    resources = svc.get("resources", {})
    env = svc.get("environment", {})
    
    # Build unit file
    lines = [
        f"[Unit]",
        f"Description={svc.get('description', name)}",
    ]
    
    # Dependencies
    deps = svc.get("dependencies", {}).get("services", [])
    if deps:
        lines.append(f"After={' '.join(deps + ['network.target'])}")
        lines.append(f"Requires={' '.join(deps)}")
    else:
        lines.append("After=network.target")
    
    lines.append("")
    lines.append("[Service]")
    lines.append(f"Type=simple")
    lines.append(f"ExecStart={binary['path']} {' '.join(binary.get('args', []))}")
    lines.append(f"WorkingDirectory={binary.get('working_dir', '/tmp')}")
    lines.append(f"Restart={restart['policy']}")
    lines.append(f"RestartSec={restart.get('delay', 10)}")
    
    # Resource limits
    mem = resources.get("memory", {})
    if "limit" in mem:
        lines.append(f"MemoryMax={mem['limit']}")
    if "reservation" in mem:
        lines.append(f"MemoryMin={mem['reservation']}")
    
    cpu = resources.get("cpu", {})
    if "limit" in cpu:
        lines.append(f"CPUQuota={float(cpu['limit']) * 100}%")
    
    # Environment
    for key, value in env.items():
        lines.append(f"Environment={key}={value}")
    
    # Logging
    log_driver = svc.get("logging", {}).get("driver", "journald")
    if log_driver == "journald":
        lines.append("StandardOutput=journal")
        lines.append("StandardError=journal")
    
    lines.append("")
    lines.append("[Install]")
    lines.append("WantedBy=multi-user.target")
    
    return "\n".join(lines)

def main(manifest_path):
    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)
    
    errors = validate_manifest(manifest)
    if errors:
        print("❌ Validation failed:")
        for err in errors:
            print(f"  - {err}")
        return 1
    
    unit = generate_systemd_unit(manifest)
    svc_name = manifest["service"]["name"]
    output_path = f"/tmp/{svc_name}.service"
    
    with open(output_path, "w") as f:
        f.write(unit)
    
    print(f"✅ Generated: {output_path}")
    print("\n--- Unit File ---")
    print(unit)
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 manifest-to-systemd.py <manifest.yaml>")
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
```

**Sample manifest for testing:**
```yaml
service:
  name: plato-tile-server
  version: "2.1.0"
  description: "PLATO tile ingestion and query API"
  binary:
    path: /opt/fleet/plato/server
    args: ["--config", "/etc/fleet/plato.yml"]
    working_dir: /var/lib/plato
  environment:
    PLATO_PORT: "8847"
    PLATO_LOG_LEVEL: "info"
  dependencies:
    services:
      - redis-cache
  health_check:
    type: http
    endpoint: "http://localhost:8847/status"
    interval: 30
    timeout: 5
    retries: 3
  resources:
    memory:
      limit: "512M"
      reservation: "256M"
    cpu:
      limit: "1.0"
  restart:
    policy: always
    max_attempts: 5
    delay: 10
  logging:
    driver: journald
```

**Verification:**
```bash
# Save sample manifest
cat > /tmp/plato-manifest.yaml <<'EOF'
service:
  name: plato-tile-server
  version: "2.1.0"
  description: "PLATO tile ingestion and query API"
  binary:
    path: /opt/fleet/plato/server
    args: ["--config", "/etc/fleet/plato.yml"]
    working_dir: /var/lib/plato
  environment:
    PLATO_PORT: "8847"
    PLATO_LOG_LEVEL: "info"
  dependencies:
    services:
      - redis-cache
  health_check:
    type: http
    endpoint: "http://localhost:8847/status"
    interval: 30
    timeout: 5
    retries: 3
  resources:
    memory:
      limit: "512M"
      reservation: "256M"
    cpu:
      limit: "1.0"
  restart:
    policy: always
    max_attempts: 5
    delay: 10
  logging:
    driver: journald
EOF

python3 manifest-to-systemd.py /tmp/plato-manifest.yaml
# Expected:
# ✅ Generated: /tmp/plato-tile-server.service
# 
# --- Unit File ---
# [Unit]
# Description=PLATO tile ingestion and query API
# After=redis-cache network.target
# Requires=redis-cache
# 
# [Service]
# Type=simple
# ExecStart=/opt/fleet/plato/server --config /etc/fleet/plato.yml
# ...
```

---

## Exercise: Scaffolding Level 3 (Officer)

**Task:** Build a Python class that manages fleet architecture: stores ADRs, validates service manifests, generates reports, and maintains a strategy index.

**Solution:**
```python
#!/usr/bin/env python3
"""fleet-command.py — fleet architecture and strategy management"""

import json, yaml, re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class FleetCommand:
    def __init__(self, base_dir="/tmp/fleet-command"):
        self.base = Path(base_dir)
        self.adrs_dir = self.base / "adrs"
        self.manifests_dir = self.base / "manifests"
        self.strategies_dir = self.base / "strategies"
        self.reports_dir = self.base / "reports"
        
        for d in [self.adrs_dir, self.manifests_dir, self.strategies_dir, self.reports_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        self.index = self._load_index()
    
    def _load_index(self):
        path = self.base / "index.json"
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return {"adrs": [], "manifests": [], "strategies": [], "reports": []}
    
    def _save_index(self):
        with open(self.base / "index.json", "w") as f:
            json.dump(self.index, f, indent=2)
    
    def create_adr(self, number, title, status="Proposed", deciders="TBD", context="", decision="", consequences=""):
        """Create a new Architecture Decision Record."""
        slug = re.sub(r'[^\w\s-]', '', title).strip().lower().replace(' ', '-')
        filename = f"adr-{number:03d}-{slug}.md"
        path = self.adrs_dir / filename
        
        content = f"""# ADR-{number:03d}: {title}

**Status:** {status}  
**Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Deciders:** {deciders}

## Context

{context or "What is the issue that we're seeing that is motivating this decision?"}

## Decision

{decision or "What is the change that we're proposing or have agreed to implement?"}

## Consequences

{consequences or "What becomes easier or more difficult to do because of this change?"}

## Alternatives Considered

- Alternative 1: Brief description
- Alternative 2: Brief description

## Notes

Additional context, links, or references.
"""
        with open(path, "w") as f:
            f.write(content)
        
        self.index["adrs"].append({
            "number": number,
            "title": title,
            "status": status,
            "file": str(path),
            "created": datetime.now().isoformat(),
        })
        self._save_index()
        
        return str(path)
    
    def validate_manifest(self, manifest_path):
        """Validate a service manifest."""
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)
        
        errors = []
        svc = manifest.get("service", {})
        
        required_top = ["name", "binary", "health_check", "restart"]
        for key in required_top:
            if key not in svc:
                errors.append(f"Missing required field: service.{key}")
        
        if "path" not in svc.get("binary", {}):
            errors.append("Missing service.binary.path")
        
        hc = svc.get("health_check", {})
        if hc.get("type") == "http" and "endpoint" not in hc:
            errors.append("HTTP health check requires 'endpoint'")
        
        restart = svc.get("restart", {})
        if restart.get("policy") not in ["always", "on-failure", "no"]:
            errors.append("restart.policy must be: always, on-failure, no")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "service_name": svc.get("name", "unknown"),
        }
    
    def register_manifest(self, manifest_path):
        """Register a manifest after validation."""
        result = self.validate_manifest(manifest_path)
        if not result["valid"]:
            return result
        
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)
        
        svc_name = manifest["service"]["name"]
        dest = self.manifests_dir / f"{svc_name}.yaml"
        
        import shutil
        shutil.copy(manifest_path, dest)
        
        self.index["manifests"].append({
            "name": svc_name,
            "file": str(dest),
            "registered": datetime.now().isoformat(),
        })
        self._save_index()
        
        return {"valid": True, "registered": str(dest)}
    
    def create_strategy(self, title, objective, tactics, escalation=None, metrics=None):
        """Create a strategy document."""
        slug = re.sub(r'[^\w\s-]', '', title).strip().lower().replace(' ', '-')
        filename = f"strategy-{slug}.md"
        path = self.strategies_dir / filename
        
        tactics_md = "\n".join(f"### {i+1}. {t['name']}\n\n{t['description']}" for i, t in enumerate(tactics))
        
        escalation_md = ""
        if escalation:
            rows = "\n".join(f"| {e['scenario']} | {e['action']} | {e['owner']} |" for e in escalation)
            escalation_md = f"""## Escalation

| Scenario | Action | Owner |
|----------|--------|-------|
{rows}

"""
        
        metrics_md = ""
        if metrics:
            items = "\n".join(f"- **{k}:** {v}" for k, v in metrics.items())
            metrics_md = f"""## Metrics

{items}

"""
        
        content = f"""# Strategy: {title}

**Author:** Fleet Command  
**Version:** 1.0  
**Date:** {datetime.now().strftime('%Y-%m-%d')}

## Objective

{objective}

## Tactics

{tactics_md}

{escalation_md}{metrics_md}## Review

This strategy is reviewed monthly. Next review: {(datetime.now().replace(day=1) + __import__('datetime').timedelta(days=32)).strftime('%Y-%m-%d')}.
"""
        with open(path, "w") as f:
            f.write(content)
        
        self.index["strategies"].append({
            "title": title,
            "file": str(path),
            "created": datetime.now().isoformat(),
        })
        self._save_index()
        
        return str(path)
    
    def generate_report(self):
        """Generate comprehensive fleet architecture report."""
        report = {
            "generated": datetime.now().isoformat(),
            "fleet": "cocapn-main",
            "summary": {
                "adrs": len(self.index["adrs"]),
                "manifests": len(self.index["manifests"]),
                "strategies": len(self.index["strategies"]),
            },
            "adrs": self.index["adrs"],
            "manifests": self.index["manifests"],
            "strategies": self.index["strategies"],
            "health": self._assess_health(),
        }
        
        path = self.reports_dir / f"fleet-report-{datetime.now().strftime('%Y%m%d')}.json"
        with open(path, "w") as f:
            json.dump(report, f, indent=2)
        
        return report, str(path)
    
    def _assess_health(self):
        """Assess fleet architecture health."""
        issues = []
        
        # ADR health
        accepted_adrs = sum(1 for a in self.index["adrs"] if a["status"] == "Accepted")
        if accepted_adrs < len(self.index["adrs"]) * 0.5:
            issues.append("Many ADRs not yet accepted")
        
        # Manifest health
        for m in self.index["manifests"]:
            result = self.validate_manifest(m["file"])
            if not result["valid"]:
                issues.append(f"Invalid manifest: {m['name']}")
        
        # Strategy age
        old_strategies = []
        for s in self.index["strategies"]:
            created = datetime.fromisoformat(s["created"])
            if (datetime.now() - created).days > 30:
                old_strategies.append(s["title"])
        if old_strategies:
            issues.append(f"Strategies needing review: {', '.join(old_strategies)}")
        
        return {
            "status": "healthy" if not issues else "needs_attention",
            "issues": issues,
        }
    
    def get_service_manifest(self, name):
        """Retrieve a registered service manifest."""
        path = self.manifests_dir / f"{name}.yaml"
        if path.exists():
            with open(path) as f:
                return yaml.safe_load(f)
        return None

if __name__ == '__main__':
    cmd = FleetCommand()
    
    # Create an ADR
    adr = cmd.create_adr(
        number=15,
        title="Use SQLite for Agent State Storage",
        status="Accepted",
        deciders="CCC, Oracle1",
        context="Agent state currently lives in flat files. We need querying.",
        decision="Adopt SQLite for structured agent state with JSON columns.",
        consequences="Simpler than PostgreSQL, portable, but no concurrent write scaling."
    )
    print(f"Created ADR: {adr}")
    
    # Create a strategy
    strategy = cmd.create_strategy(
        title="Agent Onboarding Flow",
        objective="New agents reach productive capability within 30 minutes of spawning.",
        tactics=[
            {"name": "Self-Discovery", "description": "Agent explores MUD rooms and documents confusion."},
            {"name": "Shell Clone", "description": "Agent clones a reference git-agent shell as starting template."},
            {"name": "First Task", "description": "Agent receives a scoped, verifiable first assignment."},
        ],
        escalation=[
            {"scenario": "Agent stuck >10 min", "action": "Auto-spawn helper agent", "owner": "CCC"},
            {"scenario": "Agent reports confusion", "action": "Human ping + log attach", "owner": "Casey"},
        ],
        metrics={
            "Time to first tile": "<15 min",
            "Self-sufficiency rate": ">80%",
        }
    )
    print(f"Created Strategy: {strategy}")
    
    # Generate report
    report, path = cmd.generate_report()
    print(f"\nFleet Report: {path}")
    print(f"ADRs: {report['summary']['adrs']}")
    print(f"Manifests: {report['summary']['manifests']}")
    print(f"Strategies: {report['summary']['strategies']}")
    print(f"Health: {report['health']['status']}")
    
    # Show index
    print(f"\nFleet Index: {cmd.base}/index.json")
```

**Verification:**
```bash
python3 fleet-command.py
# Expected:
# Created ADR: /tmp/fleet-command/adrs/adr-015-use-sqlite-for-agent-state-storage.md
# Created Strategy: /tmp/fleet-command/strategies/strategy-agent-onboarding-flow.md
# 
# Fleet Report: /tmp/fleet-command/reports/fleet-report-20260505.json
# ADRs: 1
# Manifests: 0
# Strategies: 1
# Health: healthy
# 
# Fleet Index: /tmp/fleet-command/index.json

# Check the generated files
cat /tmp/fleet-command/index.json | python3 -m json.tool
cat /tmp/fleet-command/adrs/adr-015-use-sqlite-for-agent-state-storage.md
cat /tmp/fleet-command/reports/fleet-report-20260505.json | python3 -m json.tool
```

---

## Instructor Notes

### Common Mistakes

1. **ADRs without consequences:** An ADR that only lists the decision is incomplete. Always document trade-offs.
2. **Manifests missing resource limits:** Services without memory/cpu limits can consume all host resources.
3. **Strategies without metrics:** A strategy that can't be measured is a wish, not a plan.
4. **Hardcoding paths:** Fleet tools should accept `--base-dir` or use environment variables, not assume `/tmp`.
5. **No version in manifests:** Services without version fields make rollback impossible.

### Extension Ideas

- Add a `fleet diff` command that compares two manifests and shows configuration drift
- Build a markdown linter for ADRs that enforces structure (must have Context + Decision + Consequences)
- Generate Terraform/Ansible configs from fleet manifests for multi-node deployment
- Add a `fleet simulate` mode that dry-runs service startup without modifying systemd
- Create a web UI that renders the fleet index as an interactive topology graph
- Integrate with GitHub Issues to auto-create tickets for "Accepted" ADRs that need implementation
- Add a `fleet audit` command that checks all registered manifests against current systemd state

---

*CCC 🦀 | Fleet Curriculum Designer*
*2026-05-05*
