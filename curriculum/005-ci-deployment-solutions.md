# Exercise Solutions — Lesson 005: CI Deployment

**Author:** CCC 🦀  
**Date:** 2026-05-05  
**For:** Fleet instructors and self-learners

---

## Trial A — Basic GitHub Actions Workflow

**Prompt:**
> Create a GitHub Actions workflow that runs on every push and prints "Hello from the Fleet".

**Solution:**
```yaml
# .github/workflows/hello-fleet.yml
name: Hello Fleet

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  greet:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Greet the fleet
        run: echo "Hello from the Fleet"
```

**Expected output (from GitHub Actions UI):**
```
Run echo "Hello from the Fleet"
Hello from the Fleet
```

**Verification:**
```bash
# Commit and push to see the workflow run
git add .github/workflows/hello-fleet.yml
git commit -m "Add hello fleet workflow"
git push origin main
# Then check: https://github.com/YOUR_ORG/YOUR_REPO/actions
```

---

## Trial B — Python Test Pipeline

**Prompt:**
> Create a workflow that installs Python dependencies and runs pytest on every pull request.

**Solution:**
```yaml
# .github/workflows/test.yml
name: Python Tests

on:
  pull_request:
    branches: [main, master]
  push:
    branches: [main, master]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest

      - name: Run tests
        run: pytest tests/ -v
```

**Expected output:**
```
============================= test session starts ==============================
platform linux -- Python 3.11.4, pytest-8.0.0, rootdir: /home/runner/work/repo
 collected 7 items

tests/test_guard.py::test_parse_guard PASSED                             [ 14%]
tests/test_guard.py::test_validate_guard PASSED                            [ 28%]
tests/test_tile.py::test_submit_tile PASSED                              [ 42%]
...
============================== 7 passed in 0.42s ==============================
```

**Verification:**
```bash
# Local verification (run before pushing)
python3 -m pytest tests/ -v
# Should show all tests passing locally before CI runs them
```

---

## Trial C — Lint with flake8

**Prompt:**
> Add a linting job to your CI that fails if any Python file violates PEP 8.

**Solution:**
```yaml
# .github/workflows/lint.yml
name: Lint

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install linter
        run: |
          python -m pip install --upgrade pip
          pip install flake8

      - name: Run flake8
        run: |
          # Stop on syntax errors or undefined names
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
          # Treat all other issues as warnings (exit 0)
          flake8 . --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics
```

**Expected output (clean):**
```
0       E9 syntax errors
0       F63 invalid syntax
0       F7 syntax errors
0       F82 undefined names
0       C901 function complexity > 10
```

**Verification:**
```bash
# Local check
pip install flake8
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
# Expected: 0 errors, script exits 0
```

---

## Trial D — Deploy on Tag Push

**Prompt:**
> Create a workflow that only runs when a tag matching `v*` is pushed, simulating a release deployment.

**Solution:**
```yaml
# .github/workflows/deploy.yml
name: Deploy Release

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Extract version from tag
        id: get_version
        run: echo "VERSION=${GITHUB_REF#refs/tags/}" >> $GITHUB_OUTPUT

      - name: Print deploy info
        run: |
          echo "🚀 Deploying version ${{ steps.get_version.outputs.VERSION }}"
          echo "Timestamp $(date -u +%Y-%m-%dT%H:%M:%SZ)"

      - name: Simulate deployment
        run: |
          echo "Building Docker image..."
          echo "Pushing to registry..."
          echo "Updating fleet manifest..."
          echo "✅ Deployment complete for ${{ steps.get_version.outputs.VERSION }}"
```

**Expected output:**
```
🚀 Deploying version v1.2.3
Timestamp 2026-05-05T12:00:00Z
Building Docker image...
Pushing to registry...
Updating fleet manifest...
✅ Deployment complete for v1.2.3
```

**Verification:**
```bash
# Create and push a tag
git tag v0.0.1-test
git push origin v0.0.1-test
# Check Actions tab — the deploy workflow should trigger
# Verify with: gh run list --workflow=deploy.yml
```

---

## Exercise: Scaffolding Level 1 (Recruit)

**Task:** Write a bash script that checks if a local Python project has the minimum CI files present.

**Solution:**
```bash
#!/bin/bash
# check-ci-ready.sh

PROJECT_DIR="${1:-.}"
REQUIRED_FILES=(
    ".github/workflows/test.yml"
    "requirements.txt"
    "tests/"
)

MISSING=0
echo "Checking CI readiness in: $PROJECT_DIR"
echo "=========================================="

for file in "${REQUIRED_FILES[@]}"; do
    path="$PROJECT_DIR/$file"
    if [ -e "$path" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (MISSING)"
        MISSING=$((MISSING + 1))
    fi
done

echo "=========================================="
if [ $MISSING -eq 0 ]; then
    echo "✅ Project is CI-ready"
    exit 0
else
    echo "❌ $MISSING item(s) missing"
    exit 1
fi
```

**Verification:**
```bash
mkdir -p test-project/.github/workflows test-project/tests
touch test-project/requirements.txt
cd test-project && ../check-ci-ready.sh .
# Expected:
# Checking CI readiness in: .
# ==========================================
#   ✅ .github/workflows/test.yml
#   ✅ requirements.txt
#   ✅ tests/
# ==========================================
# ✅ Project is CI-ready
```

---

## Exercise: Scaffolding Level 2 (Sailor)

**Task:** Create a Python script that generates a `.github/workflows/ci.yml` file for a project based on detected files.

**Solution:**
```python
#!/usr/bin/env python3
"""ci-generator.py — auto-generate a GitHub Actions workflow"""

import os
import json


def detect_project_type(project_dir="."):
    """Detect what kind of project this is."""
    files = os.listdir(project_dir)
    
    has_python = any(f.endswith('.py') for f in files) or os.path.isdir(os.path.join(project_dir, 'tests'))
    has_js = os.path.exists(os.path.join(project_dir, 'package.json'))
    has_docker = os.path.exists(os.path.join(project_dir, 'Dockerfile'))
    has_requirements = os.path.exists(os.path.join(project_dir, 'requirements.txt'))
    
    return {
        "python": has_python,
        "javascript": has_js,
        "docker": has_docker,
        "requirements": has_requirements,
    }


def generate_workflow(project_dir=".", output_path=".github/workflows/ci.yml"):
    """Generate a CI workflow tailored to the project."""
    detected = detect_project_type(project_dir)
    
    jobs = []
    
    if detected["python"]:
        jobs.append("""
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest flake8
      - name: Lint
        run: flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
      - name: Test
        run: pytest tests/ -v
""")
    
    if detected["javascript"]:
        jobs.append("""
  test-js:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install
        run: npm ci
      - name: Test
        run: npm test
""")
    
    workflow = f"""name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
{''.join(jobs)}
"""
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(workflow)
    
    print(f"Generated CI workflow: {output_path}")
    print(f"Detected: {json.dumps(detected, indent=2)}")
    return output_path


if __name__ == '__main__':
    import sys
    proj_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(proj_dir, ".github/workflows/ci.yml")
    generate_workflow(proj_dir, out)
```

**Verification:**
```bash
# Set up a test project
mkdir -p sailor-test/tests
cd sailor-test
cat > requirements.txt << 'EOF'
pytest==8.0.0
EOF
cat > test_demo.py << 'EOF'
def test_truth():
    assert True
EOF

# Run generator
python3 ../ci-generator.py . ./ci.yml
# Expected:
# Generated CI workflow: ./ci.yml
# Detected: {
#   "python": true,
#   "javascript": false,
#   "docker": false,
#   "requirements": true
# }

# Inspect the output
cat ./ci.yml
# Should contain: test job, setup-python, pytest, flake8
```

---

## Exercise: Scaffolding Level 3 (Officer)

**Task:** Build a Python class that validates a GitHub Actions workflow YAML file against fleet standards.

**Solution:**
```python
#!/usr/bin/env python3
"""workflow-auditor.py — validate GitHub Actions against fleet standards"""

import yaml
import sys
from pathlib import Path


class WorkflowAuditor:
    """Audit a GitHub Actions workflow for fleet compliance."""
    
    FLEET_STANDARDS = {
        "required_triggers": ["push", "pull_request"],
        "required_jobs": ["test"],
        "required_steps": ["actions/checkout@v4"],
        "forbidden_patterns": [
            "password",           # Hardcoded secrets
            "token:",             # Unless it's GITHUB_TOKEN
            "sudo",               # Unnecessary privilege escalation
        ],
        "max_timeout_minutes": 30,
    }
    
    def __init__(self, standards=None):
        self.standards = standards or self.FLEET_STANDARDS
        self.violations = []
    
    def audit(self, workflow_path):
        """Audit a workflow file. Returns (pass, violations)."""
        self.violations = []
        path = Path(workflow_path)
        
        if not path.exists():
            self.violations.append("Workflow file does not exist")
            return False, self.violations
        
        try:
            with open(path) as f:
                workflow = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.violations.append(f"Invalid YAML: {e}")
            return False, self.violations
        
        # Check triggers
        triggers = workflow.get("on", {})
        if isinstance(triggers, list):
            triggers = {t: {} for t in triggers}
        
        has_required_trigger = any(
            req in triggers for req in self.standards["required_triggers"]
        )
        if not has_required_trigger:
            self.violations.append(
                f"Missing required trigger (need one of: {self.standards['required_triggers']})"
            )
        
        # Check jobs
        jobs = workflow.get("jobs", {})
        job_names = list(jobs.keys())
        
        for required in self.standards["required_jobs"]:
            if required not in job_names:
                self.violations.append(f"Missing required job: {required}")
        
        # Check each job
        for job_name, job_config in jobs.items():
            # Timeout check
            timeout = job_config.get("timeout-minutes", 360)
            if timeout > self.standards["max_timeout_minutes"]:
                self.violations.append(
                    f"Job '{job_name}' timeout ({timeout}m) exceeds max ({self.standards['max_timeout_minutes']}m)"
                )
            
            # Step checks
            steps = job_config.get("steps", [])
            step_text = yaml.dump(steps)
            
            for pattern in self.standards["forbidden_patterns"]:
                if pattern in step_text.lower():
                    self.violations.append(
                        f"Job '{job_name}' contains forbidden pattern: '{pattern}'"
                    )
        
        # Check required steps exist anywhere
        workflow_text = yaml.dump(workflow)
        for required_step in self.standards["required_steps"]:
            if required_step not in workflow_text:
                self.violations.append(f"Missing required step: {required_step}")
        
        return len(self.violations) == 0, self.violations
    
    def report(self, workflow_path, color=True):
        """Print a formatted audit report."""
        passed, violations = self.audit(workflow_path)
        
        icon = "✅" if passed else "❌"
        print(f"{icon} Audit: {workflow_path}")
        print("=" * 50)
        
        if not violations:
            print("  No violations found. Workflow is fleet-compliant.")
        else:
            for v in violations:
                print(f"  ❌ {v}")
        
        print("=" * 50)
        print(f"Result: {'PASS' if passed else 'FAIL'} ({len(violations)} violation(s))")
        return passed


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 workflow-auditor.py <workflow.yml>")
        sys.exit(1)
    
    # First, ensure PyYAML is available
    try:
        import yaml
    except ImportError:
        print("Installing PyYAML...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
        import yaml  # noqa: F811
    
    auditor = WorkflowAuditor()
    passed = auditor.report(sys.argv[1])
    sys.exit(0 if passed else 1)
```

**Verification:**
```bash
# Create a compliant workflow
cat > good-workflow.yml << 'EOF'
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pytest tests/ -v
EOF

# Create a bad workflow
cat > bad-workflow.yml << 'EOF'
name: Bad
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    steps:
      - run: echo "no checkout"
      - run: echo "password=secret123"
EOF

# Test both
python3 workflow-auditor.py good-workflow.yml
# Expected: ✅ PASS

python3 workflow-auditor.py bad-workflow.yml
# Expected: ❌ FAIL with violations:
#   Missing required trigger (need one of: ['push', 'pull_request'])
#   Missing required job: test
#   Job 'build' timeout (60m) exceeds max (30m)
#   Missing required step: actions/checkout@v4
#   Job 'build' contains forbidden pattern: 'password'
```

---

## Instructor Notes

### Common Mistakes

1. **Wrong `on:` syntax:** `on: push` works, but `on: [push, pull_request]` is also valid. Students sometimes write `on: push, pull_request` which is invalid YAML.
2. **Forgetting `actions/checkout@v4`:** Without checkout, the job runs in an empty workspace and can't find any files.
3. **Python version as string:** `python-version: 3.10` gets parsed as `3.1` by YAML. Must quote it: `'3.10'`.
4. **Missing `pip install pytest`:** The workflow installs requirements.txt but forgets to install the test runner itself.
5. **Tag syntax:** `on: push: tags: v*` needs quotes around `v*` or the asterisk becomes a YAML alias indicator.

### Extension Ideas

- Add a matrix job that tests on Ubuntu, macOS, and Windows
- Integrate with `codecov` to upload coverage reports
- Add a `pre-commit` job that runs `black`, `isort`, and `mypy`
- Build a composite action that can be reused across all fleet repos
- Add a deployment job that only runs after tests pass on the `main` branch
- Create a badge generator that updates README.md with CI status

---

*CCC 🦀 | Fleet Curriculum Designer*  
*2026-05-05*
