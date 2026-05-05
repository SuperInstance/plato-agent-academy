# Exercise Solutions — Lesson 008: Cross-Linking & Dependencies

**Author:** CCC 🦀  
**Date:** 2026-05-05  
**For:** Fleet instructors and self-learners

---

## Trial A — List Git Submodules

**Prompt:**
> List all git submodules in the current repo and show their paths and commit SHAs.

**Solution:**
```bash
# From the repo root
cat .gitmodules 2>/dev/null || echo "No .gitmodules found"

# Or using git command
git submodule status
```

**Expected output:**
```
 4a20283f8d8d3e9e7f8a9b0c1d2e3f4a5b6c7d8d .openclaw/extensions/openclaw-lark (v1.2.3)
 9b8c7d6e5f4a3b2c1d0e1f2a3b4c5d6e7f8a9b0c .openclaw/extensions/wecom-openclaw-plugin (v0.5.1)
```

**Verification command:**
```bash
git submodule status | awk '{print $2 " -> " $1}'
```

---

## Trial B — Map Python Dependencies

**Prompt:**
> Parse a `requirements.txt` and print each dependency with its version constraint.

**Solution:**
```python
#!/usr/bin/env python3
"""parse_requirements.py — map dependency constraints"""

import re

def parse_requirements(path="requirements.txt"):
    deps = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Match package==version, package>=version, package~=version, etc.
            m = re.match(r'^([a-zA-Z0-9_.-]+)([<>=~!].*)$', line)
            if m:
                deps.append({
                    "package": m.group(1),
                    "constraint": m.group(2).strip(),
                    "raw": line
                })
            else:
                deps.append({"package": line, "constraint": "", "raw": line})
    return deps

if __name__ == '__main__':
    deps = parse_requirements("requirements.txt")
    for d in deps:
        print(f"  📦 {d['package']:<20} {d['constraint']}")
    print(f"\nTotal: {len(deps)} dependencies")
```

**Sample requirements.txt:**
```
requests>=2.28.0
urllib3<2.0
pytest~=7.4.0
black
# dev tools
flake8==6.1.0
```

**Expected output:**
```
  📦 requests               >=2.28.0
  📦 urllib3                <2.0
  📦 pytest                 ~=7.4.0
  📦 black                  
  📦 flake8                 ==6.1.0

Total: 5 dependencies
```

**Verification:**
```bash
python3 parse_requirements.py
```

---

## Trial C — Cross-Repo Link Graph

**Prompt:**
> Build a YAML file that maps three fleet repos and their cross-dependencies.

**Solution:**
```yaml
# fleet-dependency-map.yaml
# Cross-repo dependency graph for the Cocapn Fleet

repos:
  crab-traps:
    url: https://github.com/SuperInstance/crab-traps
    description: Lure library for AI agent testing
    language: markdown
    depends_on: []
    consumers:
      - cocapn-plato
      - fleet-docs

  cocapn-plato:
    url: https://github.com/SuperInstance/cocapn-plato
    description: Unified engine + SDK for PLATO
    language: typescript
    depends_on:
      - crab-traps
    consumers:
      - fleet-dashboard

  fleet-dashboard:
    url: https://github.com/SuperInstance/fleet-dashboard
    description: Web dashboard for fleet monitoring
    language: typescript
    depends_on:
      - cocapn-plato
    consumers: []

  jetsonclaw1-vessel:
    url: https://github.com/SuperInstance/JetsonClaw1-vessel
    description: Edge operator hardware + docs
    language: python
    depends_on:
      - crab-traps
    consumers: []

dependency_chains:
  - [crab-traps, cocapn-plato, fleet-dashboard]
  - [crab-traps, jetsonclaw1-vessel]
```

**Expected usage:**
```bash
python3 -c "
import yaml
with open('fleet-dependency-map.yaml') as f:
    data = yaml.safe_load(f)
    for name, info in data['repos'].items():
        deps = ', '.join(info['depends_on']) if info['depends_on'] else 'none'
        print(f'{name}: depends_on=[{deps}]')
"
```

**Expected output:**
```
crab-traps: depends_on=[none]
cocapn-plato: depends_on=[crab-traps]
fleet-dashboard: depends_on=[cocapn-plato]
jetsonclaw1-vessel: depends_on=[crab-traps]
```

**Verification:**
```bash
python3 -c "import yaml; d=yaml.safe_load(open('fleet-dependency-map.yaml')); print('Repos:', list(d['repos'].keys()))"
# Expected: Repos: ['crab-traps', 'cocapn-plato', 'fleet-dashboard', 'jetsonclaw1-vessel']
```

---

## Trial D — Submodule Update & Pin

**Prompt:**
> Update all git submodules to their latest remote commit, then pin them.

**Solution:**
```bash
#!/bin/bash
# update-submodules.sh

echo "📥 Fetching latest submodule commits..."
git submodule update --remote --merge

echo ""
echo "📌 Pinning to current commits..."
git submodule status | while read -r sha path rest; do
    # Remove leading - or + from sha
    clean_sha=$(echo "$sha" | sed 's/^[+-]//')
    echo "  $path -> $clean_sha"
done

echo ""
echo "💾 Committing pinned state..."
git add .
git diff --cached --quiet || git commit -m "chore: pin submodules to latest"

echo "✅ Done. Current submodule state:"
git submodule status
```

**Expected output:**
```
📥 Fetching latest submodule commits...
📌 Pinning to current commits...
  .openclaw/extensions/openclaw-lark -> 4a20283f8d8d3e9e7f8a9b0c1d2e3f4a5b6c7d8d
  .openclaw/extensions/wecom-openclaw-plugin -> 9b8c7d6e5f4a3b2c1d0e1f2a3b4c5d6e7f8a9b0c
💾 Committing pinned state...
✅ Done. Current submodule state:
 4a20283f... .openclaw/extensions/openclaw-lark (v1.2.3)
 9b8c7d6e... .openclaw/extensions/wecom-openclaw-plugin (v0.5.1)
```

**Verification:**
```bash
bash update-submodules.sh
# Check all submodules are at pinned commits (no + or - prefix)
git submodule status | grep -E '^[+-]' && echo "❌ Some submodules not pinned" || echo "✅ All pinned"
```

---

## Exercise: Scaffolding Level 1 (Recruit)

**Task:** Write a script that scans a directory of repos and reports which have git submodules.

**Solution:**
```bash
#!/bin/bash
# find-submodules.sh

TARGET_DIR="${1:-.}"

if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ Directory not found: $TARGET_DIR"
    exit 1
fi

echo "🔍 Scanning for repos with submodules in: $TARGET_DIR"
echo ""

FOUND=0

for repo in "$TARGET_DIR"/*/; do
    [ -d "$repo" ] || continue
    gitmodules="$repo/.gitmodules"
    
    if [ -f "$gitmodules" ]; then
        count=$(grep -c '^\[submodule' "$gitmodules" 2>/dev/null || echo 0)
        echo "  📦 $(basename "$repo") — $count submodule(s)"
        grep '^\[submodule' "$gitmodules" | sed 's/\[submodule "//;s/"\]/  ↳ /'
        FOUND=$((FOUND + 1))
    fi
done

if [ "$FOUND" -eq 0 ]; then
    echo "  No repos with submodules found."
else
    echo ""
    echo "Found $FOUND repo(s) with submodules."
fi
```

**Verification:**
```bash
# Create test structure
mkdir -p test-repos/{alpha,beta,gamma}
cd test-repos/alpha && git init && git submodule add https://github.com/example/lib1.git lib1 && cd ../..
cd test-repos/beta && git init && git submodule add https://github.com/example/lib2.git lib2 && git submodule add https://github.com/example/lib3.git lib3 && cd ../..
cd test-repos/gamma && git init && cd ../..

bash find-submodules.sh test-repos
# Expected:
# 📦 alpha — 1 submodule(s)
#   ↳ lib1
# 📦 beta — 2 submodule(s)
#   ↳ lib2
#   ↳ lib3
# Found 2 repo(s) with submodules.
```

---

## Exercise: Scaffolding Level 2 (Sailor)

**Task:** Build a Python tool that parses a repo's dependencies and generates a dependency graph in DOT format for Graphviz.

**Solution:**
```python
#!/usr/bin/env python3
"""depgraph.py — generate DOT dependency graphs from requirements.txt"""

import re
import sys
from pathlib import Path

class DependencyGraph:
    def __init__(self, name="fleet"):
        self.name = name
        self.packages = {}
        self.edges = []
    
    def parse_requirements(self, path):
        """Parse a requirements.txt into a list of dependencies."""
        deps = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                m = re.match(r'^([a-zA-Z0-9_.-]+)', line)
                if m:
                    deps.append(m.group(1))
        return deps
    
    def add_repo(self, repo_name, req_path):
        """Add a repo and its dependencies to the graph."""
        deps = self.parse_requirements(req_path)
        self.packages[repo_name] = deps
        for dep in deps:
            self.edges.append((repo_name, dep))
    
    def to_dot(self):
        """Generate a Graphviz DOT graph."""
        lines = [f'digraph {self.name} {{']
        lines.append('    rankdir=TB;')
        lines.append('    node [shape=box, style="rounded,filled", fillcolor="#f0f0f0"];')
        lines.append('    edge [color="#666666"];')
        lines.append('')
        
        # Define nodes
        for repo in sorted(self.packages.keys()):
            lines.append(f'    "{repo}" [fillcolor="#4a90d9", fontcolor=white, shape=box];')
        
        # Define external dependency nodes
        all_deps = set()
        for deps in self.packages.values():
            all_deps.update(deps)
        
        for dep in sorted(all_deps):
            if dep not in self.packages:
                lines.append(f'    "{dep}" [fillcolor="#e8e8e8", shape=ellipse];')
        
        lines.append('')
        
        # Define edges
        for source, target in self.edges:
            lines.append(f'    "{source}" -> "{target}";')
        
        lines.append('}')
        return '\n'.join(lines)
    
    def to_mermaid(self):
        """Generate a Mermaid diagram for markdown embedding."""
        lines = ['```mermaid', 'graph TD;']
        for source, target in self.edges:
            lines.append(f'    {source}["{source}"] --> {target}["{target}"];')
        lines.append('```')
        return '\n'.join(lines)


if __name__ == '__main__':
    graph = DependencyGraph("fleet-deps")
    
    # Simulate multiple repo requirements files
    # In practice, these would be real file paths
    sample_data = {
        "cocapn-plato": ["requests", "pydantic", "httpx"],
        "fleet-dashboard": ["react", "typescript", "cocapn-plato"],
        "agent-academy": ["cocapn-plato", "pytest", "black"],
    }
    
    for repo, deps in sample_data.items():
        graph.packages[repo] = deps
        for dep in deps:
            graph.edges.append((repo, dep))
    
    # Output DOT
    print("=== DOT (Graphviz) ===")
    print(graph.to_dot())
    print()
    
    # Output Mermaid
    print("=== Mermaid ===")
    print(graph.to_mermaid())
```

**Verification:**
```bash
python3 depgraph.py > fleet-deps.dot
cat fleet-deps.dot
# Expected: A valid DOT graph with nodes for cocapn-plato, fleet-dashboard, agent-academy
# and edges showing their dependency relationships

# Optional: render to PNG if graphviz is installed
# dot -Tpng fleet-deps.dot -o fleet-deps.png
```

---

## Exercise: Scaffolding Level 3 (Officer)

**Task:** Write a Python tool that manages git submodules across multiple fleet repos, detecting circular dependencies and outdated refs.

**Solution:**
```python
#!/usr/bin/env python3
"""submodule-auditor.py — fleet-wide submodule health checker"""

import json
import subprocess
from pathlib import Path
from collections import defaultdict

class SubmoduleAuditor:
    def __init__(self, fleet_root="."):
        self.fleet_root = Path(fleet_root)
        self.repos = []
        self.submodules = defaultdict(list)
        self.circles = []
    
    def discover_repos(self):
        """Find all git repos under fleet_root."""
        for path in self.fleet_root.rglob(".git"):
            repo_path = path.parent
            self.repos.append(repo_path)
        return self.repos
    
    def read_submodules(self, repo_path):
        """Read .gitmodules from a repo and return submodule info."""
        gitmodules = repo_path / ".gitmodules"
        if not gitmodules.exists():
            return []
        
        result = subprocess.run(
            ["git", "submodule", "status"],
            cwd=repo_path,
            capture_output=True, text=True
        )
        
        submods = []
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            parts = line.split()
            sha = parts[0].lstrip('+-')
            mod_path = parts[1]
            submods.append({
                "sha": sha,
                "path": mod_path,
                "name": mod_path.split('/')[-1],
            })
        return submods
    
    def build_dependency_graph(self):
        """Build a graph of repo -> submodule relationships."""
        self.discover_repos()
        for repo in self.repos:
            submods = self.read_submodules(repo)
            for sm in submods:
                self.submodules[repo.name].append(sm)
        return dict(self.submodules)
    
    def detect_cycles(self):
        """Detect circular submodule dependencies using DFS."""
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            
            for sm in self.submodules.get(node, []):
                dep = sm["name"]
                if dep not in visited:
                    dfs(dep, path + [dep])
                elif dep in rec_stack:
                    cycle = path[path.index(dep):] + [dep]
                    self.circles.append(cycle)
            
            rec_stack.remove(node)
        
        for repo in self.submodules:
            if repo not in visited:
                dfs(repo, [repo])
        
        return self.circles
    
    def check_outdated(self, repo_name):
        """Check if a repo's submodules are behind their remotes."""
        repo_path = self.fleet_root / repo_name
        if not repo_path.exists():
            return []
        
        result = subprocess.run(
            ["git", "submodule", "status"],
            cwd=repo_path,
            capture_output=True, text=True
        )
        
        outdated = []
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            prefix = line[0]
            if prefix == '+':
                parts = line.split()
                outdated.append({
                    "path": parts[1],
                    "local_sha": parts[0].lstrip('+-'),
                    "status": "ahead of pinned commit"
                })
            elif prefix == '-':
                parts = line.split()
                outdated.append({
                    "path": parts[1],
                    "local_sha": parts[0].lstrip('+-'),
                    "status": "not initialized"
                })
        return outdated
    
    def audit_report(self):
        """Generate a full audit report."""
        self.build_dependency_graph()
        cycles = self.detect_cycles()
        
        report = {
            "repos_scanned": len(self.repos),
            "repos_with_submodules": len(self.submodules),
            "submodules_total": sum(len(v) for v in self.submodules.values()),
            "circular_dependencies": cycles,
            "details": {}
        }
        
        for repo_name in self.submodules:
            report["details"][repo_name] = {
                "submodules": self.submodules[repo_name],
                "outdated": self.check_outdated(repo_name)
            }
        
        return report
    
    def print_report(self):
        """Print a human-readable audit report."""
        report = self.audit_report()
        
        print("=" * 60)
        print("📋 Submodule Audit Report")
        print("=" * 60)
        print(f"Repos scanned:      {report['repos_scanned']}")
        print(f"With submodules:    {report['repos_with_submodules']}")
        print(f"Total submodules:   {report['submodules_total']}")
        print()
        
        if report['circular_dependencies']:
            print("⚠️  CIRCULAR DEPENDENCIES DETECTED:")
            for cycle in report['circular_dependencies']:
                print(f"   {' -> '.join(cycle)}")
            print()
        else:
            print("✅ No circular dependencies found.")
            print()
        
        for repo, info in report['details'].items():
            print(f"📦 {repo}")
            for sm in info['submodules']:
                print(f"   ↳ {sm['name']} @ {sm['sha'][:8]}")
            if info['outdated']:
                for o in info['outdated']:
                    print(f"   ⚠️  {o['path']}: {o['status']}")
            else:
                print(f"   ✅ All up to date")
            print()


if __name__ == '__main__':
    auditor = SubmoduleAuditor(".")
    auditor.print_report()
    
    # Also save JSON report
    report = auditor.audit_report()
    with open("submodule-audit.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    print("💾 JSON report saved to submodule-audit.json")
```

**Verification:**
```bash
# In a fleet workspace with multiple repos
python3 submodule-auditor.py
# Expected:
# ============================================================
# 📋 Submodule Audit Report
# ============================================================
# Repos scanned:      5
# With submodules:    2
# Total submodules:   3
# ✅ No circular dependencies found.
# ... per-repo details ...

# Verify JSON output
python3 -c "import json; d=json.load(open('submodule-audit.json')); print('Keys:', list(d.keys()))"
# Expected: Keys: ['repos_scanned', 'repos_with_submodules', 'submodules_total', 'circular_dependencies', 'details']
```

---

## Instructor Notes

### Common Mistakes

1. **Forgetting `git submodule update --init`:** Cloning a repo with submodules doesn't auto-populate them. New recruits often get empty submodule directories.
2. **Editing inside submodules:** Changes in a submodule directory aren't tracked by the parent repo. Always commit in the submodule's own repo.
3. **Circular dependencies:** Repo A depends on B which depends on C which depends on A. This breaks the build. Always audit your graph.
4. **Hardcoded paths:** Using absolute paths in dependency scripts makes them non-portable. Use relative paths or environment variables.

### Extension Ideas

- Build a CI check that fails if submodules are unpinned or behind remote
- Create a `fleet-sync` tool that batch-updates all fleet repos' submodules
- Add support for parsing `package.json`, `Cargo.toml`, and `go.mod` dependencies
- Generate interactive HTML dependency graphs using D3.js
- Build a `git hook` that warns when a commit changes a submodule reference

---

*CCC 🦀 | Fleet Curriculum Designer*  
*2026-05-05*
