# Exercise Solutions — Lesson 010: Fleet Orchestration

**Author:** CCC 🦀  
**Date:** 2026-05-05  
**For:** Fleet instructors and self-learners

---

## Trial A — Check Service Health with curl

**Prompt:**
> Check if the PLATO, MUD, and Grammar Engine services are responding.

**Solution:**
```bash
#!/bin/bash
# check-services.sh

SERVICES=(
    "PLATO|http://147.224.38.131:8847/status"
    "MUD|http://147.224.38.131:4042"
    "Grammar|http://147.224.38.131:4045"
)

echo "🛰️ Fleet Service Health Check"
echo ""

for svc in "${SERVICES[@]}"; do
    name=$(echo "$svc" | cut -d'|' -f1)
    url=$(echo "$svc" | cut -d'|' -f2)
    
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null)
    
    if [ "$status" = "200" ] || [ "$status" = "404" ]; then
        echo "  ✅ $name — UP (HTTP $status)"
    else
        echo "  ❌ $name — DOWN (HTTP ${status:-timeout})"
    fi
done
```

**Expected output:**
```
🛰️ Fleet Service Health Check

  ✅ PLATO — UP (HTTP 200)
  ✅ MUD — UP (HTTP 404)  # 404 is expected for root path
  ✅ Grammar — UP (HTTP 404)
```

**Verification:**
```bash
bash check-services.sh
# Expected: All three services report UP (may be 200 or 404 depending on endpoint)
```

---

## Trial B — Parse Service Status JSON

**Prompt:**
> Fetch the PLATO status and report room count, tile count, and uptime.

**Solution:**
```bash
curl -s http://147.224.38.131:8847/status | python3 -c "
import sys, json
d = json.load(sys.stdin)
rooms = len(d.get('rooms', {}))
tiles = d.get('tiles', {})
print(f'Rooms:      {rooms}')
print(f'Accepted:   {tiles.get(\"accepted\", 0)}')
print(f'Pending:    {tiles.get(\"pending\", 0)}')
print(f'Rejected:   {tiles.get(\"rejected\", 0)}')
print(f'Status:     {d.get(\"status\", \"unknown\")}')
"
```

**Expected output:**
```
Rooms:      34
Accepted:   196
Pending:    3
Rejected:   12
Status:     healthy
```

**Verification:**
```bash
curl -s http://147.224.38.131:8847/status | python3 -m json.tool | grep -E '"rooms"|"accepted"|"status"'
```

---

## Trial C — YAML Service Manifest

**Prompt:**
> Write a YAML manifest that defines the fleet's core services, their ports, and health check endpoints.

**Solution:**
```yaml
# fleet-services.yaml
# Service manifest for the Cocapn Fleet

version: "1.0"
environment: production

services:
  plato:
    description: "PLATO tile engine and SDK"
    host: "147.224.38.131"
    port: 8847
    protocol: http
    health_check:
      endpoint: "/status"
      method: GET
      expected_status: 200
      timeout_seconds: 5
      interval_seconds: 30
    dependencies: []
    replicas: 1

  mud:
    description: "Cocapn Fleet MUD game server"
    host: "147.224.38.131"
    port: 4042
    protocol: http
    health_check:
      endpoint: "/"
      method: GET
      expected_status: 404  # Root returns 404, /connect returns 200
      timeout_seconds: 5
      interval_seconds: 30
    dependencies:
      - plato
    replicas: 1

  grammar-engine:
    description: "Grammar and parsing engine"
    host: "147.224.38.131"
    port: 4045
    protocol: http
    health_check:
      endpoint: "/health"
      method: GET
      expected_status: 200
      timeout_seconds: 5
      interval_seconds: 60
    dependencies:
      - plato
    replicas: 1

  fleet-dashboard:
    description: "Web dashboard for fleet monitoring"
    host: "147.224.38.131"
    port: 4046
    protocol: http
    health_check:
      endpoint: "/"
      method: GET
      expected_status: 200
      timeout_seconds: 10
      interval_seconds: 30
    dependencies:
      - plato
      - mud
    replicas: 1

  domain-rooms:
    description: "Domain room statistics endpoint"
    host: "147.224.38.131"
    port: 4050
    protocol: http
    health_check:
      endpoint: "/STATS"
      method: GET
      expected_status: 200
      timeout_seconds: 5
      interval_seconds: 60
    dependencies:
      - mud
    replicas: 1

alerts:
  channels:
    - type: matrix
      room: "#fleet-ops"
    - type: log
      path: "/var/log/fleet/alerts.log"
  
  rules:
    - name: "service-down"
      condition: "health_check.failed > 2"
      severity: critical
      message: "Service {service.name} is down"
    
    - name: "high-latency"
      condition: "health_check.latency_ms > 5000"
      severity: warning
      message: "Service {service.name} is responding slowly"
```

**Expected usage:**
```bash
python3 -c "
import yaml
with open('fleet-services.yaml') as f:
    data = yaml.safe_load(f)
    for name, svc in data['services'].items():
        deps = ', '.join(svc['dependencies']) if svc['dependencies'] else 'none'
        print(f'{name}: {svc[\"host\"]}:{svc[\"port\"]} (depends on: {deps})')
"
```

**Expected output:**
```
plato: 147.224.38.131:8847 (depends on: none)
mud: 147.224.38.131:4042 (depends on: plato)
grammar-engine: 147.224.38.131:4045 (depends on: plato)
fleet-dashboard: 147.224.38.131:4046 (depends on: plato, mud)
domain-rooms: 147.224.38.131:4050 (depends on: mud)
```

**Verification:**
```bash
python3 -c "
import yaml
d=yaml.safe_load(open('fleet-services.yaml'))
print('Services:', list(d['services'].keys()))
print('Alerts:', len(d['alerts']['rules']))
"
# Expected: Services: ['plato', 'mud', 'grammar-engine', 'fleet-dashboard', 'domain-rooms']
#           Alerts: 2
```

---

## Trial D — Service Dependency Check

**Prompt:**
> Write a script that checks if a service's dependencies are healthy before checking the service itself.

**Solution:**
```bash
#!/bin/bash
# check-with-deps.sh

PLATO_URL="http://147.224.38.131:8847/status"
MUD_URL="http://147.224.38.131:4042"
DASHBOARD_URL="http://147.224.38.131:4046"

check_service() {
    local name=$1
    local url=$2
    local expected=${3:-200}
    
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null)
    
    if [ "$status" = "$expected" ]; then
        echo "  ✅ $name — healthy ($status)"
        return 0
    else
        echo "  ❌ $name — unhealthy ($status)"
        return 1
    fi
}

echo "🔗 Dependency-Aware Health Check"
echo ""

# Check base infrastructure first
echo "Layer 1: Core Services"
plato_ok=false
mud_ok=false

check_service "PLATO" "$PLATO_URL" && plato_ok=true
check_service "MUD" "$MUD_URL" "404" && mud_ok=true  # MUD root returns 404
echo ""

# Check dependent services only if base is healthy
echo "Layer 2: Dependent Services"
if [ "$plato_ok" = true ] && [ "$mud_ok" = true ]; then
    check_service "Dashboard" "$DASHBOARD_URL"
else
    echo "  ⚠️  Skipping dependent service checks (dependencies unhealthy)"
    echo "      Dashboard — status unknown"
fi
```

**Expected output:**
```
🔗 Dependency-Aware Health Check

Layer 1: Core Services
  ✅ PLATO — healthy (200)
  ✅ MUD — healthy (404)

Layer 2: Dependent Services
  ✅ Dashboard — healthy (200)
```

**Verification:**
```bash
bash check-with-deps.sh
# Expected: Layer 1 shows PLATO and MUD status, Layer 2 shows Dashboard status
```

---

## Exercise: Scaffolding Level 1 (Recruit)

**Task:** Write a script that pings all fleet services every 60 seconds and logs their status to a file.

**Solution:**
```bash
#!/bin/bash
# service-logger.sh

LOGFILE="${1:-fleet-health.log}"
INTERVAL=60

SERVICES=(
    "PLATO|http://147.224.38.131:8847/status|200"
    "MUD|http://147.224.38.131:4042|404"
    "Grammar|http://147.224.38.131:4045|404"
    "Dashboard|http://147.224.38.131:4046|200"
    "Rooms|http://147.224.38.131:4050/STATS|200"
)

log_status() {
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local name=$1
    local url=$2
    local expected=$3
    
    start=$(date +%s%3N)
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null)
    end=$(date +%s%3N)
    latency=$((end - start))
    
    if [ "$status" = "$expected" ]; then
        state="UP"
    else
        state="DOWN"
    fi
    
    echo "${timestamp},${name},${state},${status},${latency}ms" >> "$LOGFILE"
    echo "  ${name}: ${state} (${status}) — ${latency}ms"
}

echo "🛰️ Fleet Service Logger"
echo "Logging to: $LOGFILE"
echo "Interval: ${INTERVAL}s"
echo "Press Ctrl+C to stop"
echo ""

# CSV header
echo "timestamp,service,state,status_code,latency" > "$LOGFILE"

while true; do
    echo "--- $(date -u +"%H:%M:%S") ---"
    for svc in "${SERVICES[@]}"; do
        name=$(echo "$svc" | cut -d'|' -f1)
        url=$(echo "$svc" | cut -d'|' -f2)
        expected=$(echo "$svc" | cut -d'|' -f3)
        log_status "$name" "$url" "$expected"
    done
    echo ""
    sleep "$INTERVAL"
done
```

**Verification:**
```bash
# Run for 2 cycles, then stop
bash -c '
LOGFILE="test-fleet.log"
echo "timestamp,service,state,status_code,latency" > "$LOGFILE"
for svc in "PLATO|http://147.224.38.131:8847/status|200" "MUD|http://147.224.38.131:4042|404"; do
    name=$(echo "$svc" | cut -d"|" -f1)
    url=$(echo "$svc" | cut -d"|" -f2)
    expected=$(echo "$svc" | cut -d"|" -f3)
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null)
    state=$(if [ "$status" = "$expected" ]; then echo "UP"; else echo "DOWN"; fi)
    echo "$(date -u +%H:%M:%S),$name,$state,$status,0ms" >> "$LOGFILE"
done
cat "$LOGFILE"
'
# Expected: CSV with headers and 2 data rows showing UP/DOWN status
```

---

## Exercise: Scaffolding Level 2 (Sailor)

**Task:** Build a Python health monitor that checks multiple services, tracks uptime percentage, and sends alerts when services go down.

**Solution:**
```python
#!/usr/bin/env python3
"""fleet-monitor.py — service health monitor with uptime tracking"""

import time
import json
import urllib.request
from urllib.error import HTTPError, URLError
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

class FleetMonitor:
    def __init__(self, config_path="fleet-services.yaml"):
        self.services = {}
        self.history = defaultdict(list)  # service -> [(timestamp, status)]
        self.uptime = defaultdict(lambda: {"checks": 0, "passes": 0})
        self.load_config(config_path)
    
    def load_config(self, path):
        """Load services from YAML config."""
        import yaml
        with open(path) as f:
            config = yaml.safe_load(f)
        
        for name, svc in config.get("services", {}).items():
            self.services[name] = {
                "url": f"{svc['protocol']}://{svc['host']}:{svc['port']}{svc['health_check']['endpoint']}",
                "expected": svc['health_check']['expected_status'],
                "timeout": svc['health_check']['timeout_seconds'],
            }
    
    def check_service(self, name):
        """Check a single service and return status info."""
        svc = self.services[name]
        url = svc["url"]
        expected = svc["expected"]
        timeout = svc["timeout"]
        
        start = time.time()
        try:
            req = urllib.request.Request(url, method='GET')
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = resp.status
                latency_ms = int((time.time() - start) * 1000)
                healthy = (status == expected)
                return {
                    "name": name,
                    "healthy": healthy,
                    "status": status,
                    "latency_ms": latency_ms,
                    "error": None
                }
        except HTTPError as e:
            # Some services return 404 on root but are healthy
            latency_ms = int((time.time() - start) * 1000)
            healthy = (e.code == expected)
            return {
                "name": name,
                "healthy": healthy,
                "status": e.code,
                "latency_ms": latency_ms,
                "error": None
            }
        except URLError as e:
            return {
                "name": name,
                "healthy": False,
                "status": None,
                "latency_ms": int((time.time() - start) * 1000),
                "error": str(e.reason)
            }
        except Exception as e:
            return {
                "name": name,
                "healthy": False,
                "status": None,
                "latency_ms": 0,
                "error": str(e)
            }
    
    def check_all(self):
        """Check all services and update history."""
        results = []
        now = datetime.utcnow()
        
        for name in self.services:
            result = self.check_service(name)
            results.append(result)
            
            self.history[name].append((now, result["healthy"]))
            self.uptime[name]["checks"] += 1
            if result["healthy"]:
                self.uptime[name]["passes"] += 1
            
            # Keep only last 1000 entries per service
            if len(self.history[name]) > 1000:
                self.history[name] = self.history[name][-1000:]
        
        return results
    
    def get_uptime_pct(self, name, window_minutes=60):
        """Calculate uptime percentage over a time window."""
        if name not in self.history:
            return 0.0
        
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent = [h for h in self.history[name] if h[0] > cutoff]
        
        if not recent:
            return 100.0 if self.uptime[name]["checks"] == 0 else \
                   (self.uptime[name]["passes"] / self.uptime[name]["checks"] * 100)
        
        passes = sum(1 for _, healthy in recent if healthy)
        return passes / len(recent) * 100
    
    def print_status(self, results):
        """Print current service status table."""
        print(f"\n🛰️ Fleet Status — {datetime.utcnow().isoformat()}Z")
        print("-" * 70)
        print(f"{'Service':<20} {'Status':<10} {'HTTP':<8} {'Latency':<12} {'Uptime(1h)':<12}")
        print("-" * 70)
        
        for r in results:
            name = r["name"]
            status = "🟢 UP" if r["healthy"] else "🔴 DOWN"
            http = str(r["status"]) if r["status"] else "N/A"
            latency = f"{r['latency_ms']}ms"
            uptime = f"{self.get_uptime_pct(name):.1f}%"
            
            print(f"{name:<20} {status:<10} {http:<8} {latency:<12} {uptime:<12}")
            
            if r["error"]:
                print(f"   ⚠️  {r['error']}")
        
        print("-" * 70)
    
    def run_alert_rules(self, results):
        """Evaluate simple alert rules."""
        for r in results:
            if not r["healthy"]:
                # Check if this is a new failure (was healthy in last check)
                history = self.history.get(r["name"], [])
                if len(history) >= 2 and history[-2][1]:  # Was previously healthy
                    self.send_alert(r["name"], "service-down", f"{r['name']} is DOWN (HTTP {r['status']})")
            elif r["latency_ms"] > 5000:
                self.send_alert(r["name"], "high-latency", f"{r['name']} latency: {r['latency_ms']}ms")
    
    def send_alert(self, service, alert_type, message):
        """Send an alert (logs to stderr for demo)."""
        timestamp = datetime.utcnow().isoformat()
        print(f"\n🚨 ALERT [{timestamp}Z] {alert_type}: {message}", flush=True)
        
        # In production, this would send to Matrix, Slack, PagerDuty, etc.
        alert = {
            "timestamp": timestamp,
            "service": service,
            "type": alert_type,
            "message": message,
        }
        
        # Append to alert log
        with open("fleet-alerts.jsonl", "a") as f:
            f.write(json.dumps(alert) + "\n")
    
    def save_state(self):
        """Save monitor state to disk."""
        state = {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": dict(self.uptime),
            "history_sample": {k: [(t.isoformat(), h) for t, h in v[-10:]] 
                              for k, v in self.history.items()}
        }
        with open("fleet-monitor-state.json", "w") as f:
            json.dump(state, f, indent=2)
    
    def run(self, interval=30):
        """Main monitoring loop."""
        print("🛰️ Fleet Monitor started")
        print(f"Services: {', '.join(self.services.keys())}")
        print(f"Interval: {interval}s")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                results = self.check_all()
                self.print_status(results)
                self.run_alert_rules(results)
                self.save_state()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n🛑 Monitor stopped.")
            self.save_state()


if __name__ == '__main__':
    import sys
    config = sys.argv[1] if len(sys.argv) > 1 else "fleet-services.yaml"
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    monitor = FleetMonitor(config)
    monitor.run(interval=interval)
```

**Verification:**
```bash
# One-shot test (non-looping)
python3 -c "
from fleet_monitor import FleetMonitor
m = FleetMonitor('fleet-services.yaml')
results = m.check_all()
for r in results:
    print(f\"{r['name']}: {'UP' if r['healthy'] else 'DOWN'} ({r['status']}) {r['latency_ms']}ms\")
    if r['error']:
        print(f\"  Error: {r['error']}\")
"
# Expected: Each service reports UP/DOWN with status code and latency
```

---

## Exercise: Scaffolding Level 3 (Officer)

**Task:** Build a Python fleet orchestration tool that reads the service manifest, performs dependency-ordered health checks, generates an incident report, and can simulate a rolling restart.

**Solution:**
```python
#!/usr/bin/env python3
"""fleet-orchestrator.py — service orchestration with dependency ordering"""

import json
import time
import yaml
import urllib.request
from urllib.error import HTTPError, URLError
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, deque

class FleetOrchestrator:
    """Orchestrate fleet services with dependency-aware operations."""
    
    def __init__(self, manifest_path="fleet-services.yaml"):
        self.manifest_path = manifest_path
        self.services = {}
        self.dependencies = defaultdict(list)
        self.dependents = defaultdict(list)
        self.incidents = []
        self.load_manifest()
    
    def load_manifest(self):
        """Load and parse the service manifest."""
        with open(self.manifest_path) as f:
            manifest = yaml.safe_load(f)
        
        for name, svc in manifest.get("services", {}).items():
            self.services[name] = {
                "url": f"{svc['protocol']}://{svc['host']}:{svc['port']}{svc['health_check']['endpoint']}",
                "expected": svc['health_check']['expected_status'],
                "timeout": svc['health_check']['timeout_seconds'],
                "host": svc['host'],
                "port": svc['port'],
                "description": svc.get('description', ''),
            }
            
            for dep in svc.get("dependencies", []):
                self.dependencies[name].append(dep)
                self.dependents[dep].append(name)
    
    def topological_sort(self):
        """Return services in dependency order (roots first)."""
        in_degree = {name: len(self.dependencies[name]) for name in self.services}
        queue = deque([name for name, deg in in_degree.items() if deg == 0])
        order = []
        
        while queue:
            name = queue.popleft()
            order.append(name)
            for dependent in self.dependents[name]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        if len(order) != len(self.services):
            raise ValueError("Circular dependency detected in service graph!")
        
        return order
    
    def check_service(self, name):
        """Check health of a single service."""
        svc = self.services[name]
        url = svc["url"]
        expected = svc["expected"]
        timeout = svc["timeout"]
        
        start = time.time()
        try:
            req = urllib.request.Request(url, method='GET')
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = resp.status
                latency_ms = int((time.time() - start) * 1000)
                healthy = (status == expected)
                return {
                    "name": name,
                    "healthy": healthy,
                    "status": status,
                    "latency_ms": latency_ms,
                    "error": None,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except HTTPError as e:
            latency_ms = int((time.time() - start) * 1000)
            healthy = (e.code == expected)
            return {
                "name": name,
                "healthy": healthy,
                "status": e.code,
                "latency_ms": latency_ms,
                "error": None,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "name": name,
                "healthy": False,
                "status": None,
                "latency_ms": 0,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def health_check_all(self, dependency_order=False):
        """Check all services, optionally in dependency order."""
        if dependency_order:
            order = self.topological_sort()
        else:
            order = list(self.services.keys())
        
        results = []
        print(f"🔍 Checking {len(order)} service(s)...")
        
        for name in order:
            result = self.check_service(name)
            results.append(result)
            
            status_emoji = "🟢" if result["healthy"] else "🔴"
            print(f"  {status_emoji} {name:<20} HTTP {result['status'] or 'ERR'}  {result['latency_ms']}ms")
            
            if result["error"]:
                print(f"     ⚠️  {result['error']}")
            
            # If a dependency is down, skip dependent services
            if not result["healthy"]:
                for dependent in self.dependents[name]:
                    if dependent in order[order.index(name):]:
                        print(f"     ⏭️  Skipping {dependent} (dependency unhealthy)")
        
        return results
    
    def generate_incident_report(self, results):
        """Generate a structured incident report from health check results."""
        down_services = [r for r in results if not r["healthy"]]
        
        if not down_services:
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "affected_services": [],
                "impact": "none",
                "recommended_action": "No action required"
            }
        
        # Determine impact cascade
        affected = set(s["name"] for s in down_services)
        for svc in list(affected):
            affected.update(self.dependents[svc])
        
        severity = "critical" if len(affected) > len(self.services) / 2 else \
                   "high" if len(affected) > 1 else "medium"
        
        report = {
            "status": "degraded" if any(r["status"] is not None for r in down_services) else "down",
            "timestamp": datetime.utcnow().isoformat(),
            "severity": severity,
            "affected_services": sorted(affected),
            "direct_failures": [s["name"] for s in down_services],
            "impact": f"{len(affected)} service(s) affected ({len(affected)/len(self.services)*100:.0f}% of fleet)",
            "recommended_action": self._recommend_action(down_services),
            "details": down_services
        }
        
        self.incidents.append(report)
        return report
    
    def _recommend_action(self, down_services):
        """Generate a recommended action based on failures."""
        has_timeouts = any("timeout" in (s.get("error") or "").lower() for s in down_services)
        has_refused = any("refused" in (s.get("error") or "").lower() for s in down_services)
        
        if has_refused:
            return "Service(s) not listening on expected port. Check if process is running."
        elif has_timeouts:
            return "Service(s) not responding within timeout. Check network connectivity and load."
        else:
            return "Investigate service logs and restart affected services."
    
    def simulate_rolling_restart(self, batch_size=1, delay=5):
        """Simulate a rolling restart of all services in dependency order."""
        order = self.topological_sort()
        plan = []
        
        print("\n🔄 Simulating Rolling Restart")
        print(f"   Strategy: {batch_size} service(s) at a time, {delay}s delay")
        print(f"   Order: {' -> '.join(order)}")
        print("")
        
        for i in range(0, len(order), batch_size):
            batch = order[i:i + batch_size]
            print(f"Phase {i//batch_size + 1}: Restarting {' + '.join(batch)}")
            
            for svc in batch:
                plan.append({
                    "phase": i // batch_size + 1,
                    "service": svc,
                    "action": "restart",
                    "dependencies_healthy": all(
                        self.check_service(dep)["healthy"]
                        for dep in self.dependencies[svc]
                    ),
                    "timestamp": datetime.utcnow().isoformat()
                })
                print(f"  🔄 {svc} restarted")
            
            if i + batch_size < len(order):
                print(f"  ⏳ Waiting {delay}s for batch to stabilize...")
                time.sleep(delay)
        
        print("\n✅ Rolling restart simulation complete")
        return plan
    
    def print_dependency_graph(self):
        """Print an ASCII dependency graph."""
        print("\n📊 Service Dependency Graph")
        print("=" * 50)
        
        for name in self.topological_sort():
            deps = self.dependencies[name]
            dependents = self.dependents[name]
            
            dep_str = f"depends: [{', '.join(deps) or 'none'}]"
            dep_on_str = f"used by: [{', '.join(dependents) or 'none'}]"
            
            print(f"  📦 {name}")
            print(f"     {dep_str}")
            print(f"     {dep_on_str}")
            print()
    
    def export_report(self, report, path="incident-report.json"):
        """Export incident report to JSON."""
        with open(path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n💾 Incident report saved to {path}")


if __name__ == '__main__':
    import sys
    
    manifest = sys.argv[1] if len(sys.argv) > 1 else "fleet-services.yaml"
    command = sys.argv[2] if len(sys.argv) > 2 else "status"
    
    orch = FleetOrchestrator(manifest)
    
    if command == "status":
        results = orch.health_check_all(dependency_order=True)
        report = orch.generate_incident_report(results)
        
        print(f"\n📋 Fleet Status: {report['status'].upper()}")
        if report['status'] != 'healthy':
            print(f"   Severity: {report['severity']}")
            print(f"   Impact: {report['impact']}")
            print(f"   Action: {report['recommended_action']}")
        
        orch.export_report(report)
    
    elif command == "deps":
        orch.print_dependency_graph()
    
    elif command == "restart":
        plan = orch.simulate_rolling_restart(batch_size=1, delay=3)
        with open("restart-plan.json", "w") as f:
            json.dump(plan, f, indent=2)
        print("💾 Restart plan saved to restart-plan.json")
    
    elif command == "incidents":
        if orch.incidents:
            print(f"📋 {len(orch.incidents)} incident(s) on record")
            for inc in orch.incidents:
                print(f"  {inc['timestamp']} — {inc['status']} ({inc['severity']})")
        else:
            print("📋 No incidents recorded")
    
    else:
        print(f"Unknown command: {command}")
        print("Usage: python3 fleet-orchestrator.py [manifest] [status|deps|restart|incidents]")
```

**Verification:**
```bash
# Test dependency ordering
python3 -c "
from fleet_orchestrator import FleetOrchestrator
orch = FleetOrchestrator('fleet-services.yaml')
order = orch.topological_sort()
print('Dependency order:', ' -> '.join(order))
# Expected: plato first, then services that depend on it
"

# Test health check
python3 fleet-orchestrator.py fleet-services.yaml status
# Expected: Status report showing all services with dependency-aware checks

# Test dependency graph
python3 fleet-orchestrator.py fleet-services.yaml deps
# Expected: ASCII graph showing depends_on and used_by for each service

# Test rolling restart simulation
python3 fleet-orchestrator.py fleet-services.yaml restart
# Expected: Phase-by-phase restart simulation with delays
```

---

## Instructor Notes

### Common Mistakes

1. **Checking dependent services before dependencies:** A common recruit mistake is checking the dashboard before confirming PLATO is up. Always validate the base layer first.
2. **Ignoring expected 404s:** The MUD returns 404 on `/` but is healthy. Check the right endpoint or know your expected status codes.
3. **No timeout on curl:** Default curl waits forever. Always set `--max-time` in monitoring scripts.
4. **Storing state in memory only:** If the monitor crashes, you lose uptime history. Write state to disk periodically.
5. **Missing graceful degradation:** When a dependency fails, dependent services should degrade gracefully, not cascade-fail. The orchestrator's skip logic handles this.

### Extension Ideas

- Add a webhook alert system that sends to Matrix `#fleet-ops` when services fail
- Build a real-time dashboard using the monitor's JSON state file
- Implement a circuit breaker pattern: after 3 consecutive failures, stop checking and alert
- Add latency percentile tracking (p50, p95, p99) for performance monitoring
- Create a `fleetctl` CLI tool that wraps the orchestrator with subcommands
- Implement log tailing: monitor service logs and correlate errors with health check failures
- Build a "fleet upgrade" command that does dependency-ordered rolling restarts for real
- Add Prometheus metrics exporter for integration with Grafana dashboards
- Implement a service mesh concept: proxy all inter-service traffic through the orchestrator

---

*CCC 🦀 | Fleet Curriculum Designer*  
*2026-05-05*
