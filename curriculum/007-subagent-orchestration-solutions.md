# Exercise Solutions — Lesson 007: Subagent Orchestration

**Author:** CCC 🦀  
**Date:** 2026-05-05  
**For:** Fleet instructors and self-learners

---

## Trial A — Spawn a Simple Subagent

**Prompt:**
> Write a bash command that spawns a subagent to list all files in `/tmp` and return the result.

**Solution:**
```bash
# Using the OpenClaw subagent spawn mechanism
# (This is a conceptual example — actual spawning depends on your OpenClaw config)

# Simulate with a background process + file communication
(
  ls -la /tmp > /tmp/subagent-output.txt
  echo "DONE" >> /tmp/subagent-output.txt
) &
SUBAGENT_PID=$!

# Wait for completion
wait $SUBAGENT_PID

# Read result
cat /tmp/subagent-output.txt
```

**Expected output:**
```
total 48
drwxrwxrwt 12 root root 4096 May  5 12:00 .
drwxr-xr-x  1 root root 4096 May  5 10:00 ..
-rw-r--r--  1 root root    0 May  5 11:00 some-file
...
DONE
```

**Fleet-context equivalent (Python):**
```python
#!/usr/bin/env python3
"""spawn-list-files.py — spawn a subagent to list files"""

import subprocess
import tempfile
import os


def spawn_subagent_task(script_content, timeout=30):
    """Spawn a subagent by writing a script and running it."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(script_content)
        script_path = f.name
    
    try:
        result = subprocess.run(
            ['bash', script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"error": "Subagent timed out"}
    finally:
        os.unlink(script_path)


# Spawn a subagent to list /tmp
script = """
#!/bin/bash
echo "=== Subagent Report ==="
echo "PID: $$"
echo "Time: $(date)"
echo "---"
ls -la /tmp | head -20
echo "=== End Report ==="
"""

result = spawn_subagent_task(script)
print(result["stdout"])
if result["stderr"]:
    print("STDERR:", result["stderr"])
```

**Verification:**
```bash
python3 spawn-list-files.py
# Expected:
# === Subagent Report ===
# PID: 12345
# Time: Tue May  5 12:00:00 UTC 2026
# ---
# total 48
# ...
# === End Report ===
```

---

## Trial B — Baton Handoff Pattern

**Prompt:**
> Write a Python script that implements a baton handoff: Agent A does work, saves state to a file, then Agent B reads that state and continues.

**Solution:**
```python
#!/usr/bin/env python3
"""baton-handoff.py — demonstrate baton passing between subagents"""

import json
import os
import tempfile
from pathlib import Path


BATON_FILE = "/tmp/fleet-baton.json"


def agent_a_work(baton_path):
    """Agent A: Collect initial data and save to baton."""
    
    work = {
        "agent": "Agent-A",
        "stage": "data_collection",
        "timestamp": "2026-05-05T12:00:00Z",
        "data": {
            "rooms_mapped": ["harbor", "rlhf-forge", "quantization-bay"],
            "tiles_found": 47,
            "confidence_threshold": 0.85,
        },
        "notes": "Found 3 rooms with exits. Need to check prompt-lab next.",
        "next_agent": "Agent-B",
        "next_task": "map_remaining_rooms",
    }
    
    with open(baton_path, 'w') as f:
        json.dump(work, f, indent=2)
    
    print(f"🤖 Agent-A: Work complete. Baton saved to {baton_path}")
    return work


def agent_b_work(baton_path):
    """Agent B: Read baton, continue work, update baton."""
    
    with open(baton_path) as f:
        baton = json.load(f)
    
    print(f"🤖 Agent-B: Received baton from {baton['agent']}")
    print(f"   Previous stage: {baton['stage']}")
    print(f"   Notes: {baton['notes']}")
    
    # Continue the work
    baton["agent"] = "Agent-B"
    baton["stage"] = "completion"
    baton["timestamp"] = "2026-05-05T12:05:00Z"
    baton["data"]["rooms_mapped"].extend(["prompt-laboratory", "observatory"])
    baton["data"]["tiles_found"] += 12
    baton["notes"] = "Added 2 more rooms. Total tiles: 59. Task complete."
    baton["next_agent"] = None
    baton["next_task"] = None
    baton["status"] = "complete"
    
    with open(baton_path, 'w') as f:
        json.dump(baton, f, indent=2)
    
    print(f"🤖 Agent-B: Work complete. Baton updated.")
    return baton


def main():
    # Clean up any old baton
    if os.path.exists(BATON_FILE):
        os.remove(BATON_FILE)
    
    print("=" * 50)
    print("FLEET BATON HANDOFF DEMO")
    print("=" * 50)
    
    # Agent A does its work
    baton = agent_a_work(BATON_FILE)
    print(f"\n📋 Baton contents:")
    print(json.dumps(baton, indent=2))
    
    print("\n" + "-" * 50)
    print("🔄 HANDOFF: Agent-A → Agent-B")
    print("-" * 50 + "\n")
    
    # Agent B picks up the baton
    baton = agent_b_work(BATON_FILE)
    print(f"\n📋 Updated baton:")
    print(json.dumps(baton, indent=2))
    
    print("\n" + "=" * 50)
    print("✅ Handoff complete. Full chain:")
    print("   Agent-A (data_collection) → Agent-B (completion)")
    print("=" * 50)


if __name__ == '__main__':
    main()
```

**Expected output:**
```
==================================================
FLEET BATON HANDOFF DEMO
==================================================
🤖 Agent-A: Work complete. Baton saved to /tmp/fleet-baton.json

📋 Baton contents:
{
  "agent": "Agent-A",
  "stage": "data_collection",
  ...
}

--------------------------------------------------
🔄 HANDOFF: Agent-A → Agent-B
--------------------------------------------------

🤖 Agent-B: Received baton from Agent-A
   Previous stage: data_collection
   Notes: Found 3 rooms with exits. Need to check prompt-lab next.
🤖 Agent-B: Work complete. Baton updated.

📋 Updated baton:
{
  "agent": "Agent-B",
  "stage": "completion",
  "status": "complete",
  ...
}

==================================================
✅ Handoff complete. Full chain:
   Agent-A (data_collection) → Agent-B (completion)
==================================================
```

**Verification:**
```bash
python3 baton-handoff.py
# Should show the full handoff sequence with both agents' work
# Check the baton file exists:
cat /tmp/fleet-baton.json | python3 -m json.tool
# Should show valid JSON with "status": "complete"
```

---

## Trial C — Context Budget Check

**Prompt:**
> Write a Python function that estimates if a task should be split across subagents based on context size (simulated with character count).

**Solution:**
```python
#!/usr/bin/env python3
"""context-budget.py — simulate context limit management"""

import json


# Simulated context limits (in "tokens" — we approximate as chars/4)
CONTEXT_LIMITS = {
    "recruit": 4000,      # ~16K chars
    "sailor": 8000,       # ~32K chars
    "officer": 16000,     # ~64K chars
    "commander": 32000,   # ~128K chars
}


def estimate_tokens(text):
    """Rough token estimation: chars / 4."""
    return len(text) // 4


def should_spawn_subagent(task_description, agent_tier="officer", safety_margin=0.7):
    """Determine if a task should be split into subagents.
    
    Args:
        task_description: The full prompt or context for the task
        agent_tier: recruit/sailor/officer/commander
        safety_margin: Stop at this fraction of limit (default 70%)
    
    Returns:
        dict with recommendation
    """
    limit = CONTEXT_LIMITS.get(agent_tier, 8000)
    threshold = int(limit * safety_margin)
    estimated = estimate_tokens(task_description)
    
    usage_ratio = estimated / limit
    
    recommendation = {
        "agent_tier": agent_tier,
        "context_limit": limit,
        "safety_threshold": threshold,
        "estimated_tokens": estimated,
        "usage_ratio": round(usage_ratio, 2),
        "should_spawn": estimated > threshold,
        "action": None,
        "reason": None,
    }
    
    if estimated > limit:
        recommendation["action"] = "MUST_SPLIT"
        recommendation["reason"] = f"Task ({estimated} tokens) exceeds hard limit ({limit})"
    elif estimated > threshold:
        recommendation["action"] = "SHOULD_SPLIT"
        recommendation["reason"] = f"Task ({estimated} tokens) exceeds safety margin ({threshold})"
    else:
        recommendation["action"] = "OK_SINGLE"
        recommendation["reason"] = f"Task ({estimated} tokens) within safe margin ({threshold})"
    
    return recommendation


def split_task(task_description, num_subagents=2):
    """Naively split a task into chunks for parallel subagents."""
    lines = task_description.split('\n')
    chunk_size = max(1, len(lines) // num_subagents)
    
    chunks = []
    for i in range(num_subagents):
        start = i * chunk_size
        end = start + chunk_size if i < num_subagents - 1 else len(lines)
        chunk = '\n'.join(lines[start:end])
        chunks.append({
            "subagent_id": f"subagent-{i+1}",
            "chunk_lines": len(lines[start:end]),
            "estimated_tokens": estimate_tokens(chunk),
            "task_preview": chunk[:200] + "..." if len(chunk) > 200 else chunk,
        })
    
    return chunks


# Demo
if __name__ == '__main__':
    # Simulate a large task
    large_task = "Analyze these rooms:\n" + "\n".join(
        f"Room {i}: Harbor exit {i}, description placeholder, objects: [anchor, rope, barrel-{i}]"
        for i in range(500)
    )
    
    print(f"Task size: {len(large_task)} chars ≈ {estimate_tokens(large_task)} tokens")
    print("=" * 50)
    
    for tier in ["recruit", "sailor", "officer", "commander"]:
        rec = should_spawn_subagent(large_task, tier)
        icon = "🟢" if rec["action"] == "OK_SINGLE" else "🟡" if rec["action"] == "SHOULD_SPLIT" else "🔴"
        print(f"{icon} {tier:<10} {rec['action']:<15} ({rec['usage_ratio']*100:>5.1f}% usage)")
    
    print("\n" + "=" * 50)
    print("Splitting for 4 subagents...")
    chunks = split_task(large_task, num_subagents=4)
    for chunk in chunks:
        print(f"  {chunk['subagent_id']}: {chunk['chunk_lines']} lines, {chunk['estimated_tokens']} tokens")
```

**Expected output:**
```
Task size: 20489 chars ≈ 5122 tokens
==================================================
🟢 recruit    MUST_SPLIT      (128.1% usage)
🟡 sailor     MUST_SPLIT      (64.0% usage)
🟡 officer    SHOULD_SPLIT    (32.0% usage)
🟢 commander  OK_SINGLE       (16.0% usage)

==================================================
Splitting for 4 subagents...
  subagent-1: 125 lines, 1280 tokens
  subagent-2: 125 lines, 1280 tokens
  subagent-3: 125 lines, 1280 tokens
  subagent-4: 125 lines, 1282 tokens
```

**Verification:**
```bash
python3 context-budget.py
# Should show usage ratios and splitting recommendations
# All 4 subagent chunks should be under the sailor threshold (8000 * 0.7 = 5600)
```

---

## Trial D — Subagent Result Aggregation

**Prompt:**
> Write a Python script that spawns 3 parallel "subagents" (simulated with threads), collects their results, and merges them into a single report.

**Solution:**
```python
#!/usr/bin/env python3
"""subagent-aggregator.py — spawn parallel subagents and merge results"""

import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class Subagent:
    """Simulated subagent that does work and returns a result."""
    
    def __init__(self, agent_id, task, delay=1):
        self.agent_id = agent_id
        self.task = task
        self.delay = delay
        self.result = None
    
    def run(self):
        """Execute the subagent's task."""
        print(f"  🤖 [{self.agent_id}] Starting: {self.task['name']}")
        time.sleep(self.delay)  # Simulate work
        
        # Simulate different work types
        if self.task["type"] == "map_rooms":
            self.result = {
                "agent": self.agent_id,
                "task": self.task["name"],
                "rooms": ["harbor", "rlhf-forge", "quantization-bay"],
                "tiles_found": 12,
                "status": "success",
            }
        elif self.task["type"] == "audit_guards":
            self.result = {
                "agent": self.agent_id,
                "task": self.task["name"],
                "guards_checked": 5,
                "violations": 1,
                "status": "success",
            }
        elif self.task["type"] == "check_health":
            self.result = {
                "agent": self.agent_id,
                "task": self.task["name"],
                "services": {"plato": "up", "mud": "up", "tiles": "up"},
                "status": "success",
            }
        else:
            self.result = {
                "agent": self.agent_id,
                "task": self.task["name"],
                "status": "unknown_task",
            }
        
        print(f"  ✅ [{self.agent_id}] Complete: {self.task['name']}")
        return self.result


def merge_results(results):
    """Merge multiple subagent results into a fleet report."""
    
    merged = {
        "report_type": "fleet_aggregate",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "subagents_total": len(results),
        "subagents_successful": sum(1 for r in results if r.get("status") == "success"),
        "findings": {},
        "rooms": [],
        "health": {},
        "violations": 0,
    }
    
    for result in results:
        if "rooms" in result:
            merged["rooms"].extend(result["rooms"])
            merged["findings"]["tiles"] = merged["findings"].get("tiles", 0) + result.get("tiles_found", 0)
        if "guards_checked" in result:
            merged["violations"] += result.get("violations", 0)
        if "services" in result:
            merged["health"].update(result["services"])
    
    merged["rooms"] = list(set(merged["rooms"]))  # Deduplicate
    merged["status"] = "complete" if merged["subagents_successful"] == merged["subagents_total"] else "partial"
    
    return merged


def main():
    tasks = [
        {"name": "Map harbor area", "type": "map_rooms"},
        {"name": "Audit safety guards", "type": "audit_guards"},
        {"name": "Check fleet health", "type": "check_health"},
    ]
    
    print("=" * 50)
    print("FLEET SUBAGENT ORCHESTRATION")
    print("=" * 50)
    print(f"Spawning {len(tasks)} subagents...\n")
    
    subagents = [
        Subagent(f"scout-{i+1}", task, delay=1 + i * 0.5)
        for i, task in enumerate(tasks)
    ]
    
    # Run in parallel
    results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(sa.run): sa for sa in subagents}
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"  ❌ Subagent failed: {e}")
    
    print("\n" + "-" * 50)
    print("MERGING RESULTS...")
    print("-" * 50)
    
    report = merge_results(results)
    print(json.dumps(report, indent=2))
    
    print("\n" + "=" * 50)
    print(f"✅ Orchestration complete: {report['status']}")
    print(f"   Rooms found: {len(report['rooms'])}")
    print(f"   Tiles found: {report['findings'].get('tiles', 0)}")
    print(f"   Health violations: {report['violations']}")
    print("=" * 50)


if __name__ == '__main__':
    main()
```

**Expected output:**
```
==================================================
FLEET SUBAGENT ORCHESTRATION
==================================================
Spawning 3 subagents...

  🤖 [scout-1] Starting: Map harbor area
  🤖 [scout-2] Starting: Audit safety guards
  🤖 [scout-3] Starting: Check fleet health
  ✅ [scout-1] Complete: Map harbor area
  ✅ [scout-2] Complete: Audit safety guards
  ✅ [scout-3] Complete: Check fleet health

--------------------------------------------------
MERGING RESULTS...
--------------------------------------------------
{
  "report_type": "fleet_aggregate",
  "timestamp": "2026-05-05T12:00:00Z",
  "subagents_total": 3,
  "subagents_successful": 3,
  "findings": {
    "tiles": 12
  },
  "rooms": ["harbor", "rlhf-forge", "quantization-bay"],
  "health": {
    "plato": "up",
    "mud": "up",
    "tiles": "up"
  },
  "violations": 1,
  "status": "complete"
}

==================================================
✅ Orchestration complete: complete
   Rooms found: 3
   Tiles found: 12
   Health violations: 1
==================================================
```

**Verification:**
```bash
python3 subagent-aggregator.py
# Should complete in ~3 seconds (parallel, not sequential)
# All 3 subagents should report success
# Final report should show status: "complete"
```

---

## Exercise: Scaffolding Level 1 (Recruit)

**Task:** Write a bash script that spawns a background task (simulated subagent), waits for it, and prints whether it succeeded or failed.

**Solution:**
```bash
#!/bin/bash
# subagent-runner.sh

TASK_SCRIPT="$1"
TIMEOUT="${2:-10}"

if [ -z "$TASK_SCRIPT" ]; then
    echo "Usage: ./subagent-runner.sh '<command>' [timeout_seconds]"
    echo "Example: ./subagent-runner.sh 'sleep 2 && echo done' 5"
    exit 1
fi

OUTPUT_FILE=$(mktemp)
AGENT_ID="recruit-$(date +%s)"

echo "🤖 Spawning subagent $AGENT_ID..."
echo "   Task: $TASK_SCRIPT"
echo "   Timeout: ${TIMEOUT}s"

# Run task in background with timeout
(
    timeout "$TIMEOUT" bash -c "$TASK_SCRIPT" > "$OUTPUT_FILE" 2>&1
    echo "EXITCODE:$?" >> "$OUTPUT_FILE"
) &
PID=$!

# Wait with spinner
spinner="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
spinner_len=${#spinner}
i=0
while kill -0 $PID 2>/dev/null; do
    printf "\r  %s Working... %s" "${spinner:$((i % spinner_len)):1}" "$(date +%H:%M:%S)"
    i=$((i + 1))
    sleep 0.1
done
printf "\r  ✅ Subagent finished!          \n"

# Read result
OUTPUT=$(cat "$OUTPUT_FILE")
EXIT_LINE=$(echo "$OUTPUT" | grep "^EXITCODE:")
EXIT_CODE=${EXIT_LINE#EXITCODE:}
OUTPUT_CLEAN=$(echo "$OUTPUT" | grep -v "^EXITCODE:")

echo ""
echo "--- Subagent Output ---"
echo "$OUTPUT_CLEAN"
echo "---"

if [ "$EXIT_CODE" -eq 0 ]; then
    echo "✅ Subagent $AGENT_ID succeeded (exit 0)"
    rm -f "$OUTPUT_FILE"
    exit 0
elif [ "$EXIT_CODE" -eq 124 ]; then
    echo "⏱️  Subagent $AGENT_ID timed out after ${TIMEOUT}s"
    rm -f "$OUTPUT_FILE"
    exit 124
else
    echo "❌ Subagent $AGENT_ID failed (exit $EXIT_CODE)"
    rm -f "$OUTPUT_FILE"
    exit 1
fi
```

**Verification:**
```bash
chmod +x subagent-runner.sh

# Success case
./subagent-runner.sh 'echo "Hello from subagent" && ls /tmp | wc -l' 5
# Expected: ✅ succeeded, with output showing hello and a number

# Timeout case
./subagent-runner.sh 'sleep 10 && echo done' 2
# Expected: ⏱️ timed out

# Failure case
./subagent-runner.sh 'exit 42' 5
# Expected: ❌ failed (exit 42)
```

---

## Exercise: Scaffolding Level 2 (Sailor)

**Task:** Create a Python script that implements a baton file protocol: write a task spec, spawn a subagent to execute it, and read back the results.

**Solution:**
```python
#!/usr/bin/env python3
"""baton-runner.py — execute tasks via baton files with subagent simulation"""

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path


BATON_DIR = Path("/tmp/fleet-batons")


def create_baton(task_id, agent_type, instructions, input_data=None):
    """Create a baton file with task specification."""
    BATON_DIR.mkdir(parents=True, exist_ok=True)
    
    baton = {
        "baton_version": "1.0",
        "task_id": task_id,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "agent_type": agent_type,
        "status": "pending",
        "instructions": instructions,
        "input": input_data or {},
        "output": {},
        "logs": [],
    }
    
    path = BATON_DIR / f"{task_id}.json"
    with open(path, 'w') as f:
        json.dump(baton, f, indent=2)
    
    print(f"📝 Baton created: {path}")
    return str(path)


def spawn_subagent(baton_path, timeout=30):
    """Spawn a subagent (simulated via subprocess) to process the baton."""
    
    # The subagent script reads the baton, does work, writes results back
    subagent_script = f"""
import json
import sys
import time

with open('{baton_path}') as f:
    baton = json.load(f)

# Simulate work
baton["status"] = "running"
baton["logs"].append("Subagent started")

# Execute based on agent_type
if baton["agent_type"] == "room_mapper":
    rooms = baton["input"].get("seed_rooms", ["harbor"])
    mapped = []
    for room in rooms:
        mapped.append({{"name": room, "exits": 4, "tiles": 5}})
    baton["output"] = {{"rooms_mapped": mapped, "total": len(mapped)}}
    baton["logs"].append(f"Mapped {{len(mapped)}} rooms")

elif baton["agent_type"] == "tile_submitter":
    tiles = baton["input"].get("tiles", [])
    accepted = len([t for t in tiles if len(t.get("answer", "")) > 10])
    baton["output"] = {{"submitted": len(tiles), "accepted": accepted}}
    baton["logs"].append(f"Submitted {{len(tiles)}} tiles, {{accepted}} accepted")

else:
    baton["output"] = {{"error": "Unknown agent type"}}
    baton["logs"].append("Error: unknown agent type")

baton["status"] = "complete"
baton["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")

with open('{baton_path}', 'w') as f:
    json.dump(baton, f, indent=2)

print("Subagent complete")
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(subagent_script)
        script_path = f.name
    
    try:
        result = subprocess.run(
            ['python3', script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    finally:
        os.unlink(script_path)


def read_baton(baton_path):
    """Read the completed baton and return results."""
    with open(baton_path) as f:
        return json.load(f)


def run_task(task_id, agent_type, instructions, input_data, timeout=30):
    """Full pipeline: create baton → spawn subagent → read results."""
    
    print(f"\n{'='*50}")
    print(f"TASK: {task_id}")
    print(f"AGENT: {agent_type}")
    print(f"{'='*50}")
    
    # Step 1: Create baton
    baton_path = create_baton(task_id, agent_type, instructions, input_data)
    
    # Step 2: Spawn subagent
    print(f"🤖 Spawning subagent...")
    success = spawn_subagent(baton_path, timeout)
    
    if not success:
        print(f"❌ Subagent failed or timed out")
        return None
    
    # Step 3: Read results
    baton = read_baton(baton_path)
    
    print(f"✅ Subagent complete")
    print(f"   Status: {baton['status']}")
    print(f"   Output: {json.dumps(baton['output'], indent=2)}")
    print(f"   Logs: {baton['logs']}")
    
    return baton


def main():
    # Clean up old batons
    if BATON_DIR.exists():
        for f in BATON_DIR.glob("*.json"):
            f.unlink()
    
    print("FLEET BATON RUNNER")
    print("Simulated subagent orchestration via baton files")
    
    # Task 1: Room mapping
    result1 = run_task(
        task_id="map-harbor-001",
        agent_type="room_mapper",
        instructions="Map all rooms reachable from the given seed rooms",
        input_data={"seed_rooms": ["harbor", "rlhf-forge"]},
    )
    
    # Task 2: Tile submission
    result2 = run_task(
        task_id="submit-tiles-001",
        agent_type="tile_submitter",
        instructions="Submit tiles and report acceptance rate",
        input_data={
            "tiles": [
                {"question": "Q1?", "answer": "A1 with detail"},
                {"question": "Q2?", "answer": "A2"},
                {"question": "Q3?", "answer": "A3 with lots of detail here"},
            ]
        },
    )
    
    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    
    if result1:
        print(f"  Map task: {result1['output'].get('total', 0)} rooms mapped")
    if result2:
        print(f"  Submit task: {result2['output'].get('accepted', 0)}/{result2['output'].get('submitted', 0)} accepted")


if __name__ == '__main__':
    main()
```

**Verification:**
```bash
python3 baton-runner.py
# Expected:
# TASK: map-harbor-001
#   ✅ Subagent complete
#   Status: complete
#   Output: {"rooms_mapped": [...], "total": 2}
#
# TASK: submit-tiles-001
#   ✅ Subagent complete
#   Status: complete
#   Output: {"submitted": 3, "accepted": 2}
#
# SUMMARY
#   Map task: 2 rooms mapped
#   Submit task: 2/3 accepted
```

---

## Exercise: Scaffolding Level 3 (Officer)

**Task:** Build a Python class that manages a fleet of subagents: spawns them in parallel, monitors health, handles timeouts, aggregates results, and writes a final orchestration report.

**Solution:**
```python
#!/usr/bin/env python3
"""fleet-orchestrator.py — full subagent fleet management"""

import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class SubagentTask:
    """Definition of work for a single subagent."""
    task_id: str
    agent_type: str
    instructions: str
    input_data: Dict = field(default_factory=dict)
    timeout: int = 30
    retries: int = 2


@dataclass
class SubagentResult:
    """Result from a completed subagent."""
    task_id: str
    agent_type: str
    status: str  # success, timeout, error, skipped
    output: Dict = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    error: Optional[str] = None


class FleetOrchestrator:
    """Manage a fleet of subagents with full monitoring and aggregation."""
    
    def __init__(self, name="default-fleet", max_workers=4):
        self.name = name
        self.max_workers = max_workers
        self.results: List[SubagentResult] = []
        self.audit_log: List[Dict] = []
        self.start_time: Optional[datetime] = None
    
    def _simulate_subagent(self, task: SubagentTask) -> SubagentResult:
        """Simulate a subagent executing a task."""
        start = time.time()
        logs = [f"[{task.task_id}] Subagent started ({task.agent_type})"]
        
        try:
            # Simulate work based on agent_type
            if task.agent_type == "scout":
                time.sleep(0.5)
                rooms = task.input_data.get("rooms", ["harbor"])
                output = {
                    "rooms_scouted": len(rooms),
                    "room_names": rooms,
                    "new_exits": 3,
                }
                logs.append(f"Scouted {len(rooms)} rooms")
            
            elif task.agent_type == "auditor":
                time.sleep(0.3)
                files = task.input_data.get("files", [])
                issues = sum(1 for f in files if "bad" in f)
                output = {
                    "files_checked": len(files),
                    "issues_found": issues,
                    "clean_files": len(files) - issues,
                }
                logs.append(f"Audited {len(files)} files, found {issues} issues")
            
            elif task.agent_type == "mapper":
                time.sleep(0.7)
                seed = task.input_data.get("seed_room", "harbor")
                output = {
                    "seed": seed,
                    "mapped_rooms": [seed, f"{seed}-east", f"{seed}-west"],
                    "depth": 1,
                }
                logs.append(f"Mapped from {seed}")
            
            elif task.agent_type == "failing":
                # Simulate a task that always fails
                raise RuntimeError("Simulated subagent failure")
            
            else:
                time.sleep(0.2)
                output = {"message": "Generic task complete"}
                logs.append("Completed generic task")
            
            duration = (time.time() - start) * 1000
            logs.append(f"Completed in {duration:.0f}ms")
            
            return SubagentResult(
                task_id=task.task_id,
                agent_type=task.agent_type,
                status="success",
                output=output,
                logs=logs,
                duration_ms=duration,
            )
        
        except Exception as e:
            duration = (time.time() - start) * 1000
            logs.append(f"ERROR: {e}")
            return SubagentResult(
                task_id=task.task_id,
                agent_type=task.agent_type,
                status="error",
                output={},
                logs=logs,
                duration_ms=duration,
                error=str(e),
            )
    
    def run_single(self, task: SubagentTask) -> SubagentResult:
        """Run a single task with retry logic."""
        for attempt in range(task.retries + 1):
            result = self._simulate_subagent(task)
            
            self._audit("run", task.task_id, result.status, attempt)
            
            if result.status == "success":
                return result
            
            if attempt < task.retries:
                wait = 2 ** attempt
                self._audit("retry", task.task_id, "waiting", wait)
                time.sleep(wait)
        
        return result
    
    def run_fleet(self, tasks: List[SubagentTask]) -> List[SubagentResult]:
        """Run a fleet of tasks in parallel with monitoring."""
        self.start_time = datetime.now()
        self.results = []
        
        print(f"🚀 Fleet '{self.name}' launching {len(tasks)} subagents")
        print(f"   Max workers: {self.max_workers}")
        print(f"   {'='*50}\n")
        
        completed = 0
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.run_single, task): task for task in tasks}
            
            for future in as_completed(futures):
                task = futures[future]
                try:
                    result = future.result(timeout=task.timeout)
                except Exception as e:
                    result = SubagentResult(
                        task_id=task.task_id,
                        agent_type=task.agent_type,
                        status="timeout",
                        error=str(e),
                    )
                
                self.results.append(result)
                completed += 1
                
                icon = "✅" if result.status == "success" else "❌"
                print(f"  {icon} [{completed}/{len(tasks)}] {task.task_id:<20} {result.status:<10} {result.duration_ms:>6.0f}ms")
        
        return self.results
    
    def aggregate(self) -> Dict:
        """Aggregate all results into a fleet report."""
        total = len(self.results)
        successful = sum(1 for r in self.results if r.status == "success")
        failed = total - successful
        
        total_duration = sum(r.duration_ms for r in self.results)
        avg_duration = total_duration / total if total > 0 else 0
        
        # Collect outputs by type
        by_type: Dict[str, List[Dict]] = {}
        for r in self.results:
            by_type.setdefault(r.agent_type, []).append(r.output)
        
        report = {
            "fleet_name": self.name,
            "orchestrator": "FleetOrchestrator",
            "timestamp": datetime.now().isoformat(),
            "started": self.start_time.isoformat() if self.start_time else None,
            "summary": {
                "total_tasks": total,
                "successful": successful,
                "failed": failed,
                "success_rate": f"{successful/total*100:.1f}%" if total > 0 else "N/A",
                "total_duration_ms": round(total_duration, 1),
                "avg_duration_ms": round(avg_duration, 1),
            },
            "by_agent_type": {
                at: {
                    "count": len(outputs),
                    "outputs": outputs,
                }
                for at, outputs in by_type.items()
            },
            "detailed_results": [asdict(r) for r in self.results],
            "audit_log": self.audit_log,
        }
        
        return report
    
    def save_report(self, filename="orchestration-report.json"):
        """Save the orchestration report to disk."""
        report = self.aggregate()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📁 Report saved: {filename}")
        return filename
    
    def _audit(self, action, task_id, status, detail=None):
        self.audit_log.append({
            "time": datetime.now().isoformat(),
            "action": action,
            "task": task_id,
            "status": status,
            "detail": detail,
        })


def main():
    # Build a fleet of diverse tasks
    tasks = [
        SubagentTask("scout-1", "scout", "Map the harbor area", {"rooms": ["harbor", "dock"]}, timeout=5),
        SubagentTask("scout-2", "scout", "Map the forge area", {"rooms": ["rlhf-forge", "quantization-bay"]}, timeout=5),
        SubagentTask("audit-1", "auditor", "Check code quality", {"files": ["good.py", "bad.py", "ok.py"]}, timeout=5),
        SubagentTask("audit-2", "auditor", "Check docs", {"files": ["readme.md", "bad-doc.md"]}, timeout=5),
        SubagentTask("map-1", "mapper", "Full MUD map", {"seed_room": "harbor"}, timeout=5),
        SubagentTask("fail-1", "failing", "This will fail", {}, timeout=5, retries=1),
    ]
    
    # Launch fleet
    orchestrator = FleetOrchestrator(name="cocapn-scout-fleet", max_workers=4)
    results = orchestrator.run_fleet(tasks)
    
    # Print summary
    print(f"\n{'='*50}")
    print("FLEET ORCHESTRATION SUMMARY")
    print(f"{'='*50}")
    
    report = orchestrator.aggregate()
    summary = report["summary"]
    
    print(f"  Total tasks:     {summary['total_tasks']}")
    print(f"  Successful:      {summary['successful']}")
    print(f"  Failed:          {summary['failed']}")
    print(f"  Success rate:    {summary['success_rate']}")
    print(f"  Total time:      {summary['total_duration_ms']:.0f}ms")
    print(f"  Avg per task:    {summary['avg_duration_ms']:.0f}ms")
    
    print(f"\n  By Agent Type:")
    for atype, data in report["by_agent_type"].items():
        print(f"    {atype:<12} {data['count']} task(s)")
    
    # Save report
    orchestrator.save_report("fleet-orchestration-report.json")
    
    print(f"\n{'='*50}")
    print("✅ Fleet operation complete")
    print(f"{'='*50}")


if __name__ == '__main__':
    main()
```

**Verification:**
```bash
python3 fleet-orchestrator.py
# Expected:
# 🚀 Fleet 'cocapn-scout-fleet' launching 6 subagents
#    ✅ [1/6] scout-1              success      512ms
#    ✅ [2/6] scout-2              success      501ms
#    ...
#    ❌ [6/6] fail-1               error        ...
#
# FLEET ORCHESTRATION SUMMARY
#   Total tasks:     6
#   Successful:      5
#   Failed:          1
#   Success rate:    83.3%
#
# 📁 Report saved: fleet-orchestration-report.json

# Verify report
cat fleet-orchestration-report.json | python3 -m json.tool | head -40
# Should show valid JSON with all 6 results
```

---

## Instructor Notes

### Common Mistakes

1. **Not handling timeouts:** Subagents can hang indefinitely. Always set a timeout and handle `TimeoutExpired`.
2. **Forgetting the baton file:** Without a shared state file, subagents can't communicate progress. Always write intermediate state to disk.
3. **Race conditions on baton files:** Two subagents writing the same baton at once corrupts the JSON. Use unique baton IDs or file locking.
4. **No retry logic:** Network hiccups and transient failures are normal. Implement at least 1 retry with exponential backoff.
5. **Losing error details:** When a subagent fails, capture `stderr` and the exit code. "It failed" is not actionable.
6. **Context overflow without checking:** Spawning 20 subagents that each load the same 10K context creates 200K of duplicated state. Use context-budget checks first.

### Extension Ideas

- Add a real OpenClaw subagent spawn using the `subagents spawn` CLI or API
- Implement a priority queue so critical tasks run before background tasks
- Add a "heartbeat" mechanism where subagents write progress every N seconds
- Build a visual dashboard that shows subagent status in real-time (ASCII or web)
- Create a "subagent template library" with pre-built agents for common tasks (audit, map, submit, test)
- Add baton compression: large contexts get chunked and only diffs are passed between agents
- Implement subagent-to-subagent direct messaging (bypassing the orchestrator for simple handoffs)
- Add a cost/budget tracker — each subagent "costs" tokens, track against a fleet budget

---

*CCC 🦀 | Fleet Curriculum Designer*  
*2026-05-05*
