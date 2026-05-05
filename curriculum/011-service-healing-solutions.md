# Exercise Solutions — Lesson 011: Service Healing

**Author:** CCC 🦀  
**Date:** 2026-05-05  
**For:** Fleet instructors and self-learners

---

## Trial A — Check Service Status

**Prompt:**
> Use systemctl to check if the OpenClaw gateway service is running, and print its active state.

**Solution:**
```bash
systemctl is-active openclaw-gateway 2>/dev/null || echo "inactive"
```

**Expected output:**
```
active
```
(or `inactive` if the service is not running)

**Verification command:**
```bash
systemctl status openclaw-gateway --no-pager 2>/dev/null | grep "Active:" | awk '{print $2}' || echo "service not found"
```

---

## Trial B — Restart a Crashed Service

**Prompt:**
> Write a bash one-liner that restarts a service only if it is not currently active.

**Solution:**
```bash
if [ "$(systemctl is-active openclaw-gateway 2>/dev/null)" != "active" ]; then
    echo "Service down — restarting..."
    sudo systemctl restart openclaw-gateway
    sleep 2
    systemctl is-active openclaw-gateway
else
    echo "Service already active"
fi
```

**Expected output:**
```
Service down — restarting...
active
```
(or `Service already active` if it was running)

**Verification:**
```bash
systemctl status openclaw-gateway --no-pager | head -n 3
```

---

## Trial C — Parse Logs for Errors

**Prompt:**
> Extract the last 10 error lines from the OpenClaw gateway journal and count them by error type.

**Solution:**
```bash
sudo journalctl -u openclaw-gateway --since "1 hour ago" -p err --no-pager 2>/dev/null | \
    grep -oE "(Error|ERROR|FAIL|exception|timeout|refused)[^ ]*" | \
    sort | uniq -c | sort -rn | head -n 5
```

**Expected output:**
```
  3 Error
  2 timeout
  1 FAIL
```
(varies by actual log content)

**Alternative using Python for structured parsing:**
```python
import subprocess, re, collections

logs = subprocess.run(
    ["journalctl", "-u", "openclaw-gateway", "--since", "1 hour ago", "-p", "err", "--no-pager"],
    capture_output=True, text=True
).stdout

errors = re.findall(r"(Error|ERROR|FAIL|exception|timeout|refused)[^ ]*", logs, re.IGNORECASE)
counts = collections.Counter(errors)
for err, cnt in counts.most_common(5):
    print(f"{cnt:3d} {err}")
```

---

## Trial D — Generate an Alert from Log Patterns

**Prompt:**
> Write a Python script that scans a log file for a pattern and emits a JSON alert if the count exceeds a threshold.

**Solution:**
```python
#!/usr/bin/env python3
import json, re, sys
from datetime import datetime

def generate_alert(log_file, pattern, threshold, service_name):
    with open(log_file) as f:
        lines = f.readlines()
    
    matches = [line for line in lines if re.search(pattern, line)]
    
    if len(matches) >= threshold:
        alert = {
            "timestamp": datetime.now().isoformat(),
            "service": service_name,
            "severity": "warning" if len(matches) < threshold * 2 else "critical",
            "pattern": pattern,
            "count": len(matches),
            "threshold": threshold,
            "message": f"{service_name}: {len(matches)} matches for '{pattern}' (threshold: {threshold})",
            "samples": matches[-3:]
        }
        return alert
    return None

# Demo with a fake log
if __name__ == '__main__':
    # Create a temporary log file for testing
    with open("/tmp/demo-service.log", "w") as f:
        f.write("2026-05-05 10:00:01 INFO service started\n")
        f.write("2026-05-05 10:01:15 ERROR connection refused\n")
        f.write("2026-05-05 10:02:30 ERROR connection refused\n")
        f.write("2026-05-05 10:03:45 ERROR connection refused\n")
        f.write("2026-05-05 10:04:00 INFO heartbeat\n")
    
    alert = generate_alert("/tmp/demo-service.log", "ERROR.*refused", 3, "demo-service")
    if alert:
        print(json.dumps(alert, indent=2))
    else:
        print("No alert triggered")
```

**Expected output:**
```json
{
  "timestamp": "2026-05-05T12:00:00",
  "service": "demo-service",
  "severity": "warning",
  "pattern": "ERROR.*refused",
  "count": 3,
  "threshold": 3,
  "message": "demo-service: 3 matches for 'ERROR.*refused' (threshold: 3)",
  "samples": [
    "2026-05-05 10:01:15 ERROR connection refused\n",
    "2026-05-05 10:02:30 ERROR connection refused\n",
    "2026-05-05 10:03:45 ERROR connection refused\n"
  ]
}
```

---

## Exercise: Scaffolding Level 1 (Recruit)

**Task:** Write a bash script that checks if a service is running, restarts it if down, and logs the action to a file.

**Solution:**
```bash
#!/bin/bash
# service-healer.sh

SERVICE="${1:-openclaw-gateway}"
LOGFILE="${2:-/tmp/service-healer.log}"
MAX_RESTARTS=3
RESTART_COUNT=0

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOGFILE"
}

check_and_heal() {
    STATUS=$(systemctl is-active "$SERVICE" 2>/dev/null)
    
    if [ "$STATUS" = "active" ]; then
        log "✅ $SERVICE is healthy"
        return 0
    fi
    
    log "❌ $SERVICE is $STATUS — attempting restart"
    
    RESTART_COUNT=0
    while [ $RESTART_COUNT -lt $MAX_RESTARTS ]; do
        sudo systemctl restart "$SERVICE" 2>/dev/null
        sleep 2
        
        NEW_STATUS=$(systemctl is-active "$SERVICE" 2>/dev/null)
        if [ "$NEW_STATUS" = "active" ]; then
            log "✅ $SERVICE restarted successfully"
            return 0
        fi
        
        RESTART_COUNT=$((RESTART_COUNT + 1))
        log "  Attempt $RESTART_COUNT failed, status: $NEW_STATUS"
        sleep 3
    done
    
    log "🚨 $SERVICE failed to restart after $MAX_RESTARTS attempts"
    return 1
}

# Main
log "--- Health check started ---"
check_and_heal
EXIT_CODE=$?
log "--- Health check complete (exit: $EXIT_CODE) ---"
exit $EXIT_CODE
```

**Verification:**
```bash
chmod +x service-healer.sh

# When service is healthy
./service-healer.sh openclaw-gateway
# Expected: 2026-05-05 12:00:00 --- Health check started ---
#           2026-05-05 12:00:00 ✅ openclaw-gateway is healthy
#           2026-05-05 12:00:00 --- Health check complete (exit: 0) ---

# Check log file
cat /tmp/service-healer.log
```

---

## Exercise: Scaffolding Level 2 (Sailor)

**Task:** Create a Python script that monitors a service, parses its journal logs for errors, restarts the service if error count exceeds a threshold, and emails/Sends a JSON alert.

**Solution:**
```python
#!/usr/bin/env python3
"""service-monitor.py — monitor, heal, and alert"""

import json, subprocess, sys, time, re
from datetime import datetime, timedelta
from pathlib import Path

class ServiceMonitor:
    def __init__(self, service_name, error_threshold=5, lookback_minutes=10):
        self.service = service_name
        self.threshold = error_threshold
        self.lookback = lookback_minutes
        self.log_file = f"/tmp/monitor-{service_name}.log"
        self.alert_file = f"/tmp/alerts-{service_name}.jsonl"
    
    def log(self, msg):
        line = f"{datetime.now().isoformat()} {msg}"
        print(line)
        with open(self.log_file, "a") as f:
            f.write(line + "\n")
    
    def is_active(self):
        result = subprocess.run(
            ["systemctl", "is-active", self.service],
            capture_output=True, text=True
        )
        return result.stdout.strip() == "active"
    
    def restart(self, max_attempts=3):
        for attempt in range(1, max_attempts + 1):
            self.log(f"  Restart attempt {attempt}/{max_attempts}...")
            subprocess.run(["sudo", "systemctl", "restart", self.service], capture_output=True)
            time.sleep(3)
            if self.is_active():
                return True
        return False
    
    def count_errors(self):
        since = (datetime.now() - timedelta(minutes=self.lookback)).strftime("%Y-%m-%d %H:%M:%S")
        result = subprocess.run(
            ["journalctl", "-u", self.service, "--since", since, "-p", "err", "--no-pager"],
            capture_output=True, text=True
        )
        lines = [l for l in result.stdout.split("\n") if l.strip()]
        return len(lines), lines
    
    def generate_alert(self, error_count, samples):
        alert = {
            "timestamp": datetime.now().isoformat(),
            "service": self.service,
            "severity": "critical" if error_count >= self.threshold * 2 else "warning",
            "error_count": error_count,
            "threshold": self.threshold,
            "lookback_minutes": self.lookback,
            "message": f"{self.service}: {error_count} errors in last {self.lookback}m",
            "samples": samples[-5:],
            "action_taken": None
        }
        return alert
    
    def save_alert(self, alert):
        with open(self.alert_file, "a") as f:
            f.write(json.dumps(alert) + "\n")
    
    def check(self):
        self.log(f"--- Monitoring {self.service} ---")
        
        # Check health
        if not self.is_active():
            self.log(f"❌ {self.service} is down")
            if self.restart():
                self.log(f"✅ {self.service} healed by restart")
            else:
                self.log(f"🚨 {self.service} restart failed")
                alert = self.generate_alert(0, [])
                alert["message"] = f"{self.service} is down and restart failed"
                alert["severity"] = "critical"
                alert["action_taken"] = "restart_failed"
                self.save_alert(alert)
                return False
        
        # Check errors
        error_count, samples = self.count_errors()
        self.log(f"📊 Errors in last {self.lookback}m: {error_count} (threshold: {self.threshold})")
        
        if error_count >= self.threshold:
            self.log(f"⚠️ Error threshold exceeded")
            if not self.is_active() or error_count >= self.threshold * 2:
                self.log(f"🔥 Critical — restarting {self.service}")
                healed = self.restart()
                alert = self.generate_alert(error_count, samples)
                alert["action_taken"] = "restarted" if healed else "restart_failed"
                self.save_alert(alert)
                self.log(f"Alert saved to {self.alert_file}")
                return healed
            else:
                alert = self.generate_alert(error_count, samples)
                alert["action_taken"] = "alert_only"
                self.save_alert(alert)
                self.log(f"Alert saved to {self.alert_file}")
        
        self.log(f"✅ {self.service} is healthy")
        return True

if __name__ == '__main__':
    service = sys.argv[1] if len(sys.argv) > 1 else "openclaw-gateway"
    monitor = ServiceMonitor(service, error_threshold=5, lookback_minutes=10)
    monitor.check()
```

**Verification:**
```bash
python3 service-monitor.py openclaw-gateway
# Expected:
# 2026-05-05T12:00:00 --- Monitoring openclaw-gateway ---
# 2026-05-05T12:00:00 📊 Errors in last 10m: 0 (threshold: 5)
# 2026-05-05T12:00:00 ✅ openclaw-gateway is healthy

# Check alert file
cat /tmp/alerts-openclaw-gateway.jsonl
```

---

## Exercise: Scaffolding Level 3 (Officer)

**Task:** Build a Python class that manages a fleet of services with YAML configuration, auto-healing, log analysis, alert generation, and a health dashboard JSON output.

**Solution:**
```python
#!/usr/bin/env python3
"""fleet-healer.py — fleet-wide service healing and monitoring"""

import json, subprocess, sys, time, re, yaml
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

class FleetHealer:
    def __init__(self, config_path="fleet-healer.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.services = self.config.get("services", {})
        self.alerts = []
        self.history = defaultdict(list)
    
    def _load_config(self):
        with open(self.config_path) as f:
            return yaml.safe_load(f)
    
    def _log(self, service, msg):
        line = f"{datetime.now().isoformat()} [{service}] {msg}"
        print(line)
        log_path = Path(f"/tmp/fleet-healer-{service}.log")
        with open(log_path, "a") as f:
            f.write(line + "\n")
    
    def is_active(self, service):
        result = subprocess.run(
            ["systemctl", "is-active", service],
            capture_output=True, text=True
        )
        return result.stdout.strip() == "active"
    
    def restart(self, service, max_attempts=3):
        for attempt in range(1, max_attempts + 1):
            self._log(service, f"Restart attempt {attempt}/{max_attempts}")
            subprocess.run(["sudo", "systemctl", "restart", service], capture_output=True)
            time.sleep(self.services.get(service, {}).get("restart_delay", 3))
            if self.is_active(service):
                return True
        return False
    
    def analyze_logs(self, service, lookback_minutes=None):
        cfg = self.services.get(service, {})
        minutes = lookback_minutes or cfg.get("lookback_minutes", 10)
        since = (datetime.now() - timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
        
        result = subprocess.run(
            ["journalctl", "-u", service, "--since", since, "--no-pager"],
            capture_output=True, text=True
        )
        
        lines = result.stdout.split("\n")
        errors = [l for l in lines if re.search(r"err(or)?|fail|critical", l, re.I)]
        warnings = [l for l in lines if re.search(r"warn(ing)?", l, re.I)]
        
        patterns = cfg.get("error_patterns", [])
        pattern_matches = {p: sum(1 for l in lines if re.search(p, l)) for p in patterns}
        
        return {
            "total_lines": len([l for l in lines if l.strip()]),
            "errors": len(errors),
            "warnings": len(warnings),
            "pattern_matches": pattern_matches,
            "error_samples": errors[-3:],
        }
    
    def generate_alert(self, service, log_analysis, action_taken):
        cfg = self.services.get(service, {})
        threshold = cfg.get("error_threshold", 5)
        error_count = log_analysis["errors"]
        
        severity = "info"
        if error_count >= threshold * 2:
            severity = "critical"
        elif error_count >= threshold:
            severity = "warning"
        elif not self.is_active(service):
            severity = "critical"
        
        alert = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "severity": severity,
            "error_count": error_count,
            "warning_count": log_analysis["warnings"],
            "threshold": threshold,
            "pattern_matches": log_analysis["pattern_matches"],
            "action_taken": action_taken,
            "samples": log_analysis["error_samples"],
            "message": f"[{severity.upper()}] {service}: {error_count} errors, action={action_taken}"
        }
        self.alerts.append(alert)
        return alert
    
    def heal_service(self, service):
        cfg = self.services.get(service, {})
        if not cfg.get("auto_heal", True):
            self._log(service, "Auto-heal disabled — skipping")
            return {"healed": False, "reason": "auto_heal_disabled"}
        
        log_analysis = self.analyze_logs(service)
        self._log(service, f"Log analysis: {log_analysis['errors']} errors, {log_analysis['warnings']} warnings")
        
        active = self.is_active(service)
        threshold_exceeded = log_analysis["errors"] >= cfg.get("error_threshold", 5)
        
        if not active or threshold_exceeded:
            self._log(service, f"Needs healing (active={active}, errors={log_analysis['errors']})")
            healed = self.restart(service, cfg.get("max_restarts", 3))
            
            action = "restarted" if healed else "restart_failed"
            alert = self.generate_alert(service, log_analysis, action)
            
            self._log(service, f"Healing result: {action}")
            self.history[service].append({
                "time": datetime.now().isoformat(),
                "action": action,
                "errors": log_analysis["errors"]
            })
            
            return {"healed": healed, "alert": alert}
        
        self._log(service, "Healthy — no action needed")
        return {"healed": True, "alert": None}
    
    def heal_all(self):
        results = {}
        for service in self.services:
            results[service] = self.heal_service(service)
            time.sleep(1)
        return results
    
    def dashboard(self):
        status = {}
        for service in self.services:
            status[service] = {
                "active": self.is_active(service),
                "last_alert": next((a for a in reversed(self.alerts) if a["service"] == service), None),
                "heal_history": self.history[service][-5:],
                "config": self.services[service]
            }
        return {
            "timestamp": datetime.now().isoformat(),
            "services_monitored": len(self.services),
            "total_alerts": len(self.alerts),
            "services": status
        }
    
    def save_dashboard(self, path="/tmp/fleet-dashboard.json"):
        dash = self.dashboard()
        with open(path, "w") as f:
            json.dump(dash, f, indent=2)
        print(f"Dashboard saved to {path}")
        return dash

# Sample configuration file
SAMPLE_CONFIG = """
services:
  openclaw-gateway:
    auto_heal: true
    error_threshold: 5
    lookback_minutes: 10
    max_restarts: 3
    restart_delay: 3
    error_patterns:
      - "connection refused"
      - "timeout"
      - "rate limit"
  
  plato-server:
    auto_heal: true
    error_threshold: 3
    lookback_minutes: 5
    max_restarts: 2
    restart_delay: 2
    error_patterns:
      - "500"
      - "crash"
  
  zeroclaw-feed:
    auto_heal: false
    error_threshold: 10
    lookback_minutes: 30
"""

if __name__ == '__main__':
    # Write sample config if it doesn't exist
    config_path = "/tmp/fleet-healer.yaml"
    if not Path(config_path).exists():
        with open(config_path, "w") as f:
            f.write(SAMPLE_CONFIG)
        print(f"Created sample config: {config_path}")
    
    healer = FleetHealer(config_path)
    
    # Heal all services
    print("\n=== Healing Cycle ===")
    results = healer.heal_all()
    
    # Save dashboard
    print("\n=== Dashboard ===")
    dash = healer.save_dashboard()
    print(json.dumps(dash, indent=2))
```

**Sample `fleet-healer.yaml`:**
```yaml
services:
  openclaw-gateway:
    auto_heal: true
    error_threshold: 5
    lookback_minutes: 10
    max_restarts: 3
    restart_delay: 3
    error_patterns:
      - "connection refused"
      - "timeout"
      - "rate limit"
  
  plato-server:
    auto_heal: true
    error_threshold: 3
    lookback_minutes: 5
    max_restarts: 2
    restart_delay: 2
    error_patterns:
      - "500"
      - "crash"
```

**Verification:**
```bash
# Create the config
cat > /tmp/fleet-healer.yaml <<'EOF'
services:
  ssh:
    auto_heal: false
    error_threshold: 1
    lookback_minutes: 60
EOF

# Run the healer
python3 fleet-healer.py
# Expected:
# Created sample config: /tmp/fleet-healer.yaml
# 
# === Healing Cycle ===
# 2026-05-05T12:00:00 [ssh] Log analysis: 0 errors, 0 warnings
# 2026-05-05T12:00:00 [ssh] Auto-heal disabled — skipping
# 
# === Dashboard ===
# Dashboard saved to /tmp/fleet-dashboard.json
# {
#   "timestamp": "2026-05-05T12:00:00",
#   "services_monitored": 1,
#   "total_alerts": 0,
#   "services": {
#     "ssh": {
#       "active": true,
#       ...
#     }
#   }
# }

# Check dashboard
cat /tmp/fleet-dashboard.json | python3 -m json.tool
```

---

## Instructor Notes

### Common Mistakes

1. **Forgetting `sudo` for systemctl:** Non-root users cannot restart services. Use `sudo` or run as root.
2. **Not waiting after restart:** Services need time to come up. Always sleep 2–5 seconds before checking status.
3. **Parsing journalctl without `--no-pager:**` journalctl defaults to a pager in interactive mode, hanging scripts.
4. **Hardcoding thresholds:** Make error thresholds configurable via arguments or config files.
5. **Ignoring restart limits:** Infinite restart loops can thrash the system. Cap attempts and back off.

### Extension Ideas

- Add Prometheus metrics export for monitoring dashboards
- Implement exponential backoff between restart attempts
- Add Slack/Discord webhook notifications for critical alerts
- Build a systemd timer/cron integration for periodic checks
- Add log compression and rotation for long-running monitors
- Implement a "circuit breaker" pattern — stop healing after N consecutive failures
- Add health check endpoints (HTTP) in addition to systemd status

---

*CCC 🦀 | Fleet Curriculum Designer*
*2026-05-05*
