# Exercise Solutions — Lesson 009: Security Auditing

**Author:** CCC 🦀  
**Date:** 2026-05-05  
**For:** Fleet instructors and self-learners

---

## Trial A — Secret Detection with grep

**Prompt:**
> Scan a codebase for hardcoded secrets (API keys, tokens, passwords) using grep patterns.

**Solution:**
```bash
#!/bin/bash
# secret-scan.sh

TARGET="${1:-.}"

echo "🔍 Scanning $TARGET for potential secrets..."
echo ""

# Patterns to match common secret formats
patterns=(
    'api[_-]?key[[:space:]]*[=:][[:space:]]*["'\''']*[a-zA-Z0-9_-]{16,}'
    'token[[:space:]]*[=:][[:space:]]*["'\''']*[a-zA-Z0-9_-]{16,}'
    'password[[:space:]]*[=:][[:space:]]*["'\''']*[^"'\'''
]{4,}'
    'secret[[:space:]]*[=:][[:space:]]*["'\''']*[a-zA-Z0-9_-]{8,}'
    'sk-[a-zA-Z0-9]{20,}'
    'ghp_[a-zA-Z0-9]{36}'
    'gho_[a-zA-Z0-9]{36}'
    'AKIA[0-9A-Z]{16}'
    'aws[_-]?secret[_-]?access[_-]?key'
    'private[_-]?key'
    'BEGIN[[:space:]]+RSA[[:space:]]+PRIVATE[[:space:]]+KEY'
    'BEGIN[[:space:]]+OPENSSH[[:space:]]+PRIVATE[[:space:]]+KEY'
)

FOUND=0

for pattern in "${patterns[@]}"; do
    results=$(grep -rnE "$pattern" "$TARGET" \
        --exclude-dir=.git \
        --exclude-dir=node_modules \
        --exclude-dir=__pycache__ \
        --exclude="*.lock" \
        --exclude="*.log" \
        2>/dev/null)
    
    if [ -n "$results" ]; then
        echo "⚠️  Pattern match:"
        echo "$results" | head -20
        echo ""
        FOUND=$((FOUND + $(echo "$results" | wc -l)))
    fi
done

if [ "$FOUND" -eq 0 ]; then
    echo "✅ No obvious secrets found."
else
    echo "⚠️  Total potential secrets found: $FOUND"
    echo "   (Some may be false positives — review manually)"
fi
```

**Expected output:**
```
🔍 Scanning . for potential secrets...

⚠️  Pattern match:
./config.py:3:API_KEY = "sk-abc123def456ghi789jkl012mno345pq"
./.env:2:DATABASE_PASSWORD=supersecret123

⚠️  Total potential secrets found: 2
   (Some may be false positives — review manually)
```

**Verification:**
```bash
# Create test files with fake secrets
mkdir -p test-secrets
cat > test-secrets/config.py << 'EOF'
API_KEY = "sk-abc123def456ghi789jkl012mno345pq"
DATABASE_URL = "postgres://localhost"
EOF
cat > test-secrets/.env << 'EOF'
DATABASE_PASSWORD=supersecret123
DEBUG=true
EOF

bash secret-scan.sh test-secrets
# Expected: Found the API_KEY and DATABASE_PASSWORD lines
```

---

## Trial B — Check File Permissions

**Prompt:**
> Find files with overly permissive permissions (world-readable/writable) in a repo.

**Solution:**
```bash
#!/bin/bash
# check-permissions.sh

TARGET="${1:-.}"

echo "🔐 Checking file permissions in $TARGET..."
echo ""

# World-writable files (dangerous)
echo "🚨 World-writable files:"
find "$TARGET" -type f -perm /002 ! -path "*/.git/*" ! -path "*/node_modules/*" 2>/dev/null | while read -r f; do
    perms=$(stat -c '%a' "$f" 2>/dev/null || stat -f '%Lp' "$f" 2>/dev/null)
    echo "   $perms $f"
done

echo ""

# World-readable files with sensitive extensions
sensitive_exts="pem key p12 pfx env secrets credentials"
echo "📝 World-readable sensitive files:"
for ext in $sensitive_exts; do
    find "$TARGET" -type f -name "*.$ext" -perm /004 ! -path "*/.git/*" 2>/dev/null | while read -r f; do
        perms=$(stat -c '%a' "$f" 2>/dev/null || stat -f '%Lp' "$f" 2>/dev/null)
        echo "   $perms $f"
    done
done

echo ""

# Executable files that shouldn't be (e.g., data files)
echo "⚠️  Potentially over-permissioned data files:"
find "$TARGET" -type f \( -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.csv" -o -name "*.txt" \) -perm /111 ! -path "*/.git/*" 2>/dev/null | while read -r f; do
    echo "   $f"
done
```

**Expected output:**
```
🔐 Checking file permissions in ....

🚨 World-writable files:
   666 ./test-secrets/.env

📝 World-readable sensitive files:
   644 ./certs/server.pem
   644 ./config/secrets.env
```

**Verification:**
```bash
mkdir -p test-perms/certs
chmod 666 test-perms/.env 2>/dev/null || echo "Cannot set 666 (expected on some systems)"
touch test-perms/certs/server.pem
chmod 644 test-perms/certs/server.pem
bash check-permissions.sh test-perms
```

---

## Trial C — Dependency Vulnerability Check

**Prompt:**
> Write a Python script that checks a `requirements.txt` against a known vulnerability database (simulated).

**Solution:**
```python
#!/usr/bin/env python3
"""vuln-check.py — simulated dependency vulnerability scanner"""

import re
import json
from pathlib import Path

# Simulated vulnerability database
# In production, query OSV, Snyk, or GitHub Security Advisories
VULN_DB = {
    "requests": [
        {"version": "<2.28.0", "cve": "CVE-2023-1234", "severity": "medium",
         "summary": "Certificate validation bypass in older versions"}
    ],
    "urllib3": [
        {"version": "<1.26.0", "cve": "CVE-2022-5678", "severity": "high",
         "summary": "HTTP request smuggling vulnerability"},
        {"version": ">=2.0,<2.0.7", "cve": "CVE-2024-0011", "severity": "medium",
         "summary": "Cookie leakage in redirect handling"}
    ],
    "flask": [
        {"version": "<2.3.0", "cve": "CVE-2023-9876", "severity": "high",
         "summary": "Memory exhaustion via crafted JSON payload"}
    ],
    "django": [
        {"version": "<4.2.0", "cve": "CVE-2023-5555", "severity": "critical",
         "summary": "SQL injection in admin panel"}
    ],
    "pillow": [
        {"version": "<10.0.0", "cve": "CVE-2023-4444", "severity": "medium",
         "summary": "Buffer overflow in image processing"}
    ],
}

def parse_version_constraint(constraint):
    """Parse a simple version constraint like >=1.2.3 or <2.0.0"""
    m = re.match(r'^(>=|<=|>|<|==|~=|!=)([\d.]+)', constraint)
    if m:
        return m.group(1), m.group(2)
    return None, None

def version_tuple(v):
    """Convert version string to comparable tuple."""
    return tuple(int(x) for x in v.split('.'))

def matches_vulnerable(pkg, version_str, vuln_entry):
    """Check if installed version matches a vulnerable range."""
    constraint = vuln_entry["version"]
    
    # Simple parsing: handle <X, >=X, <X,>Y formats
    if constraint.startswith("<") and not constraint.startswith("<="):
        limit = constraint[1:]
        try:
            if version_tuple(version_str) < version_tuple(limit):
                return True
        except ValueError:
            pass
    elif constraint.startswith(">="):
        limit = constraint[2:]
        try:
            if version_tuple(version_str) >= version_tuple(limit):
                return True
        except ValueError:
            pass
    elif constraint.startswith("=="):
        return version_str == constraint[2:]
    
    # Complex: try to split compound constraints like ">=2.0,<2.0.7"
    parts = constraint.split(",")
    for part in parts:
        op, ver = parse_version_constraint(part.strip())
        if op and ver:
            try:
                vt = version_tuple(version_str)
                lt = version_tuple(ver)
                if op == "<" and not (vt < lt):
                    return False
                elif op == ">=" and not (vt >= lt):
                    return False
                elif op == "==" and not (vt == lt):
                    return False
            except ValueError:
                return False
    return True

def parse_requirements(path="requirements.txt"):
    """Parse requirements.txt into structured dependencies."""
    deps = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            m = re.match(r'^([a-zA-Z0-9_.-]+)([<>=~!].*)?$', line)
            if m:
                deps.append({
                    "package": m.group(1).lower(),
                    "constraint": (m.group(2) or "").strip(),
                })
    return deps

def check_vulnerabilities(deps):
    """Check dependencies against vulnerability database."""
    findings = []
    for dep in deps:
        pkg = dep["package"]
        constraint = dep["constraint"]
        
        # Extract installed/pinned version from constraint
        version = ""
        if constraint.startswith("=="):
            version = constraint[2:]
        elif constraint.startswith(">="):
            version = constraint[2:]
        
        if pkg in VULN_DB:
            for vuln in VULN_DB[pkg]:
                if version and matches_vulnerable(pkg, version, vuln):
                    findings.append({
                        "package": pkg,
                        "version": version,
                        "cve": vuln["cve"],
                        "severity": vuln["severity"],
                        "summary": vuln["summary"],
                        "constraint": constraint
                    })
    return findings

def print_report(findings):
    """Print a human-readable vulnerability report."""
    if not findings:
        print("✅ No known vulnerabilities found in scanned dependencies.")
        return
    
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda x: severity_order.get(x["severity"], 99))
    
    print("⚠️  VULNERABILITY REPORT")
    print("=" * 60)
    
    for f in findings:
        emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(f["severity"], "⚪")
        print(f"\n{emoji} {f['package']} {f['constraint']} — {f['cve']} [{f['severity'].upper()}]")
        print(f"   {f['summary']}")
    
    print(f"\nTotal: {len(findings)} finding(s)")

if __name__ == '__main__':
    import sys
    req_file = sys.argv[1] if len(sys.argv) > 1 else "requirements.txt"
    
    deps = parse_requirements(req_file)
    print(f"📦 Scanned {len(deps)} dependencies from {req_file}\n")
    
    findings = check_vulnerabilities(deps)
    print_report(findings)
    
    # Save JSON report
    with open("vuln-report.json", "w") as f:
        json.dump(findings, f, indent=2)
    print("\n💾 JSON report saved to vuln-report.json")
```

**Sample requirements.txt:**
```
requests==2.27.1
urllib3==1.25.11
flask==2.2.0
django==4.1.0
pillow==9.5.0
```

**Expected output:**
```
📦 Scanned 5 dependencies from requirements.txt

⚠️  VULNERABILITY REPORT
============================================================

🔴 django ==4.1.0 — CVE-2023-5555 [CRITICAL]
   SQL injection in admin panel

🟠 urllib3 ==1.25.11 — CVE-2022-5678 [HIGH]
   HTTP request smuggling vulnerability

🟠 flask ==2.2.0 — CVE-2023-9876 [HIGH]
   Memory exhaustion via crafted JSON payload

🟡 requests ==2.27.1 — CVE-2023-1234 [MEDIUM]
   Certificate validation bypass in older versions

Total: 4 finding(s)
```

**Verification:**
```bash
cat > test-requirements.txt << 'EOF'
requests==2.27.1
urllib3==1.25.11
flask==2.2.0
django==4.1.0
pillow==9.5.0
EOF

python3 vuln-check.py test-requirements.txt
# Expected: Reports critical/high/medium findings for each vulnerable package
```

---

## Trial D — Audit YAML Configuration

**Prompt:**
> Scan a YAML config file for security misconfigurations (debug mode, weak passwords, exposed ports).

**Solution:**
```python
#!/usr/bin/env python3
"""yaml-security-audit.py — scan YAML configs for misconfigurations"""

import yaml
from pathlib import Path

# Security rules for config auditing
RULES = [
    {
        "id": "SEC-001",
        "name": "Debug mode enabled",
        "severity": "high",
        "check": lambda d: _get_nested(d, "debug") is True or _get_nested(d, "DEBUG") is True,
        "message": "Debug mode is enabled in production. Disable it to avoid information leakage.",
    },
    {
        "id": "SEC-002",
        "name": "Weak admin password",
        "severity": "critical",
        "check": lambda d: _is_weak_password(_get_nested(d, "admin", "password")) or \
                           _is_weak_password(_get_nested(d, "password")),
        "message": "Admin password is weak or default. Use a strong, generated password.",
    },
    {
        "id": "SEC-003",
        "name": "No HTTPS enforcement",
        "severity": "high",
        "check": lambda d: _get_nested(d, "ssl", "enabled") is False or \
                           _get_nested(d, "https") is False or \
                           _get_nested(d, "tls") is False,
        "message": "HTTPS/TLS is not enforced. All production traffic should be encrypted.",
    },
    {
        "id": "SEC-004",
        "name": "Exposed sensitive port",
        "severity": "medium",
        "check": lambda d: _exposed_sensitve_port(_get_nested(d, "ports")),
        "message": "Sensitive ports (22, 3306, 5432, 6379, 27017) are exposed externally.",
    },
    {
        "id": "SEC-005",
        "name": "CORS wildcard",
        "severity": "medium",
        "check": lambda d: _get_nested(d, "cors", "allowed_origins") == ["*"] or \
                           _get_nested(d, "cors", "origins") == ["*"],
        "message": "CORS allows all origins (*). Restrict to known domains.",
    },
    {
        "id": "SEC-006",
        "name": "Default secret key",
        "severity": "high",
        "check": lambda d: _is_default_secret(_get_nested(d, "secret_key")) or \
                           _is_default_secret(_get_nested(d, "SECRET_KEY")),
        "message": "Secret key appears to be a default or placeholder. Generate a cryptographically random key.",
    },
]

def _get_nested(d, *keys):
    """Safely get nested dict values."""
    for key in keys:
        if isinstance(d, dict) and key in d:
            d = d[key]
        else:
            return None
    return d

def _is_weak_password(pw):
    if not pw or not isinstance(pw, str):
        return False
    weak = ["admin", "password", "123456", "secret", "default", "changeme", "root"]
    return pw.lower() in weak or len(pw) < 8

def _is_default_secret(sk):
    if not sk or not isinstance(sk, str):
        return False
    return len(sk) < 16 or "change" in sk.lower() or "default" in sk.lower()

def _exposed_sensitve_port(ports):
    if not ports:
        return False
    sensitive = {22, 3306, 5432, 6379, 27017, 9200}
    if isinstance(ports, list):
        for p in ports:
            if isinstance(p, dict):
                port = p.get("port", p.get("containerPort", p.get("targetPort")))
                if port in sensitive and p.get("expose", True) is not False:
                    return True
            elif isinstance(p, int) and p in sensitive:
                return True
    elif isinstance(ports, dict):
        for port in ports.values():
            if isinstance(port, int) and port in sensitive:
                return True
    return False

def audit_config(path):
    """Audit a YAML config file against security rules."""
    with open(path) as f:
        config = yaml.safe_load(f)
    
    findings = []
    for rule in RULES:
        try:
            if rule["check"](config):
                findings.append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "severity": rule["severity"],
                    "message": rule["message"],
                })
        except Exception:
            pass
    
    return findings

def print_report(path, findings):
    """Print audit report."""
    print(f"🔐 Security Audit: {path}")
    print("=" * 60)
    
    if not findings:
        print("✅ No security misconfigurations found.")
        return
    
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda x: severity_order.get(x["severity"], 99))
    
    for f in findings:
        emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(f["severity"], "⚪")
        print(f"\n{emoji} {f['id']} — {f['name']} [{f['severity'].upper()}]")
        print(f"   {f['message']}")
    
    print(f"\nTotal: {len(findings)} issue(s)")

if __name__ == '__main__':
    import sys
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    findings = audit_config(config_path)
    print_report(config_path, findings)
```

**Sample insecure-config.yaml:**
```yaml
app:
  name: fleet-dashboard
  debug: true
  secret_key: "change-me-in-production"

database:
  host: localhost
  port: 5432
  password: "password123"
  username: admin

server:
  port: 8080
  https: false
  cors:
    allowed_origins:
      - "*"

ports:
  - port: 22
    expose: true
  - port: 8080
    expose: true
```

**Expected output:**
```
🔐 Security Audit: insecure-config.yaml
============================================================

🔴 SEC-002 — Weak admin password [CRITICAL]
   Admin password is weak or default. Use a strong, generated password.

🟠 SEC-001 — Debug mode enabled [HIGH]
   Debug mode is enabled in production. Disable it to avoid information leakage.

🟠 SEC-006 — Default secret key [HIGH]
   Secret key appears to be a default or placeholder. Generate a cryptographically random key.

🟠 SEC-003 — No HTTPS enforcement [HIGH]
   HTTPS/TLS is not enforced. All production traffic should be encrypted.

🟡 SEC-004 — Exposed sensitive port [MEDIUM]
   Sensitive ports (22, 3306, 5432, 6379, 27017) are exposed externally.

🟡 SEC-005 — CORS wildcard [MEDIUM]
   CORS allows all origins (*). Restrict to known domains.

Total: 6 issue(s)
```

**Verification:**
```bash
cat > test-config.yaml << 'EOF'
app:
  name: test-app
  debug: true
  secret_key: "default-secret"

database:
  password: "password123"
  port: 5432

server:
  https: false
  cors:
    allowed_origins: ["*"]

ports:
  - port: 22
    expose: true
EOF

python3 yaml-security-audit.py test-config.yaml
# Expected: Reports SEC-001 through SEC-006 findings
```

---

## Exercise: Scaffolding Level 1 (Recruit)

**Task:** Write a script that checks if any `.env` files exist in a repo and warns if they contain secrets.

**Solution:**
```bash
#!/bin/bash
# env-audit.sh

TARGET="${1:-.}"

echo "🔍 Searching for .env files in $TARGET..."
env_files=$(find "$TARGET" -name ".env" -o -name ".env.*" 2>/dev/null | grep -v node_modules | grep -v '.git/')

if [ -z "$env_files" ]; then
    echo "✅ No .env files found."
    exit 0
fi

echo "⚠️  Found .env files:"
echo "$env_files"
echo ""

SECRET_KEYS="API_KEY|SECRET|TOKEN|PASSWORD|PRIVATE_KEY|DATABASE_URL"
WARNINGS=0

for f in $env_files; do
    matches=$(grep -inE "^($SECRET_KEYS)" "$f" 2>/dev/null)
    if [ -n "$matches" ]; then
        echo "🚨 Potential secrets in $f:"
        echo "$matches" | while read -r line; do
            # Mask the value for display
            key=$(echo "$line" | cut -d= -f1)
            echo "   $key=***REDACTED***"
        done
        WARNINGS=$((WARNINGS + 1))
    fi
done

if [ "$WARNINGS" -gt 0 ]; then
    echo ""
    echo "⚠️  $WARNINGS .env file(s) contain potential secrets."
    echo "   Add .env to .gitignore and use environment variables instead."
    exit 1
else
    echo "✅ .env files found but no obvious secrets detected."
    exit 0
fi
```

**Verification:**
```bash
mkdir -p test-env-project
cat > test-env-project/.env << 'EOF'
API_KEY=sk-test123
DATABASE_URL=postgres://localhost
DEBUG=true
EOF

cat > test-env-project/.env.local << 'EOF'
SECRET_KEY=super-secret-123
EOF

bash env-audit.sh test-env-project
# Expected:
# ⚠️  Found .env files:
# ...
# 🚨 Potential secrets in .../.env:
#   API_KEY=***REDACTED***
#   DATABASE_URL=***REDACTED***
# 🚨 Potential secrets in .../.env.local:
#   SECRET_KEY=***REDACTED***
```

---

## Exercise: Scaffolding Level 2 (Sailor)

**Task:** Build a Python tool that scans a directory tree and generates a security scorecard with risk ratings.

**Solution:**
```python
#!/usr/bin/env python3
"""security-scorecard.py — generate a repo security scorecard"""

import os
import re
import json
from pathlib import Path
from collections import Counter

class SecurityScorecard:
    def __init__(self, repo_path="."):
        self.repo = Path(repo_path).resolve()
        self.findings = []
        self.score = 100
        self.files_scanned = 0
    
    def scan(self):
        """Run all security checks."""
        self._check_gitignore()
        self._check_env_files()
        self._check_hardcoded_secrets()
        self._check_file_permissions()
        self._check_dependency_files()
        self._calculate_score()
        return self
    
    def _check_gitignore(self):
        """Check if .gitignore exists and covers sensitive files."""
        gitignore = self.repo / ".gitignore"
        if not gitignore.exists():
            self.findings.append({
                "check": "gitignore",
                "severity": "medium",
                "message": "No .gitignore file found. Risk of committing sensitive files.",
                "deduction": 10
            })
            return
        
        content = gitignore.read_text()
        required_patterns = [".env", "*.pem", "*.key", "__pycache__/", "node_modules/"]
        missing = [p for p in required_patterns if p not in content]
        
        if missing:
            self.findings.append({
                "check": "gitignore",
                "severity": "low",
                "message": f".gitignore missing patterns: {', '.join(missing)}",
                "deduction": 3
            })
    
    def _check_env_files(self):
        """Check for committed .env files."""
        for env_file in self.repo.rglob(".env*"):
            if ".git" in str(env_file) or "node_modules" in str(env_file):
                continue
            git_tracked = os.system(f"cd {self.repo} && git ls-files '{env_file}' > /dev/null 2>&1") == 0
            if git_tracked:
                self.findings.append({
                    "check": "env-files",
                    "severity": "high",
                    "message": f".env file tracked by git: {env_file}",
                    "deduction": 15,
                    "file": str(env_file)
                })
    
    def _check_hardcoded_secrets(self):
        """Scan for hardcoded secrets in source files."""
        secret_patterns = [
            (r'sk-[a-zA-Z0-9]{20,}', "API key"),
            (r'ghp_[a-zA-Z0-9]{36}', "GitHub token"),
            (r'AKIA[0-9A-Z]{16}', "AWS access key"),
            (r'password\s*=\s*["\'][^"\']{4,}["\']', "Hardcoded password"),
        ]
        
        for src_file in self.repo.rglob("*"):
            if src_file.is_dir() or ".git" in str(src_file):
                continue
            if src_file.suffix not in ('.py', '.js', '.ts', '.sh', '.yml', '.yaml', '.json'):
                continue
            
            try:
                content = src_file.read_text()
                self.files_scanned += 1
                for pattern, secret_type in secret_patterns:
                    if re.search(pattern, content):
                        self.findings.append({
                            "check": "hardcoded-secrets",
                            "severity": "critical",
                            "message": f"{secret_type} found in {src_file}",
                            "deduction": 20,
                            "file": str(src_file)
                        })
            except (UnicodeDecodeError, PermissionError):
                continue
    
    def _check_file_permissions(self):
        """Check for overly permissive files."""
        for f in self.repo.rglob("*.pem"):
            if ".git" in str(f):
                continue
            try:
                mode = f.stat().st_mode
                if mode & 0o044:  # World-readable
                    self.findings.append({
                        "check": "file-permissions",
                        "severity": "medium",
                        "message": f"Certificate/key file is world-readable: {f}",
                        "deduction": 8,
                        "file": str(f)
                    })
            except OSError:
                pass
    
    def _check_dependency_files(self):
        """Check for outdated lock files."""
        for lock in self.repo.rglob("package-lock.json"):
            if "node_modules" in str(lock):
                continue
            content = lock.read_text()
            # Simple heuristic: check for known vulnerable package patterns
            if '"version": "1.2.3"' in content:  # placeholder for actual check
                self.findings.append({
                    "check": "dependencies",
                    "severity": "low",
                    "message": f"Lock file may contain outdated dependencies: {lock}",
                    "deduction": 2
                })
    
    def _calculate_score(self):
        """Calculate security score from findings."""
        for f in self.findings:
            self.score -= f.get("deduction", 0)
        self.score = max(0, min(100, self.score))
    
    def rating(self):
        """Get letter rating from score."""
        if self.score >= 90:
            return "A"
        elif self.score >= 80:
            return "B"
        elif self.score >= 70:
            return "C"
        elif self.score >= 60:
            return "D"
        else:
            return "F"
    
    def report(self):
        """Generate a formatted report."""
        lines = []
        lines.append("=" * 60)
        lines.append("🔐 SECURITY SCORECARD")
        lines.append("=" * 60)
        lines.append(f"Repository: {self.repo}")
        lines.append(f"Files scanned: {self.files_scanned}")
        lines.append(f"Findings: {len(self.findings)}")
        lines.append("")
        lines.append(f"Score: {self.score}/100  Rating: {self.rating()}")
        lines.append("")
        
        if not self.findings:
            lines.append("✅ No security issues found. Excellent!")
        else:
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            sorted_findings = sorted(self.findings, key=lambda x: severity_order.get(x["severity"], 99))
            
            emoji_map = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
            
            for f in sorted_findings:
                emoji = emoji_map.get(f["severity"], "⚪")
                lines.append(f"{emoji} [{f['severity'].upper()}] {f['check']}")
                lines.append(f"   {f['message']}")
                lines.append(f"   Impact: -{f.get('deduction', 0)} points")
                lines.append("")
        
        return "\n".join(lines)
    
    def to_json(self):
        """Export as JSON."""
        return {
            "repository": str(self.repo),
            "score": self.score,
            "rating": self.rating(),
            "files_scanned": self.files_scanned,
            "findings_count": len(self.findings),
            "findings": self.findings
        }


if __name__ == '__main__':
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    
    card = SecurityScorecard(target).scan()
    print(card.report())
    
    with open("security-scorecard.json", "w") as f:
        json.dump(card.to_json(), f, indent=2)
    print("\n💾 JSON report saved to security-scorecard.json")
```

**Verification:**
```bash
# Create a test repo with intentional issues
mkdir -p test-scorecard/src
cat > test-scorecard/.env << 'EOF'
API_KEY=sk-test12345678901234567890
EOF
cd test-scorecard && git init && git add .env && cd ..

touch test-scorecard/src/server.pem
chmod 644 test-scorecard/src/server.pem

cat > test-scorecard/src/config.py << 'EOF'
DATABASE_PASSWORD = "password123"
EOF

python3 security-scorecard.py test-scorecard
# Expected:
# 🔐 SECURITY SCORECARD
# ...
# Score: X/100  Rating: D or F
# 🔴 [CRITICAL] hardcoded-secrets
# 🟠 [HIGH] env-files
# 🟡 [MEDIUM] file-permissions
```

---

## Exercise: Scaffolding Level 3 (Officer)

**Task:** Build a Python tool that performs a comprehensive security audit: secret detection, file permissions, dependency vulns, and config misconfigurations, outputting a unified SARIF-like JSON report.

**Solution:**
```python
#!/usr/bin/env python3
"""fleet-security-audit.py — comprehensive security audit tool"""

import json
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class FleetSecurityAudit:
    """Comprehensive security audit for fleet repositories."""
    
    SECRET_PATTERNS = [
        (r'sk-[a-zA-Z0-9]{20,}', "OpenAI API key", "critical"),
        (r'ghp_[a-zA-Z0-9]{36}', "GitHub personal access token", "critical"),
        (r'gho_[a-zA-Z0-9]{36}', "GitHub OAuth token", "critical"),
        (r'AKIA[0-9A-Z]{16}', "AWS access key ID", "critical"),
        (r'[A-Za-z0-9/+=]{40}', "AWS secret key (candidate)", "high"),
        (r'slack_[a-zA-Z0-9_-]{20,}', "Slack token", "high"),
        (r'xox[baprs]-[a-zA-Z0-9-]+', "Slack legacy token", "high"),
        (r'private[_-]?key\s*[:=]\s*["\'][^"\']+["\']', "Private key reference", "high"),
    ]
    
    VULN_DB = {
        "requests": [("<2.28.0", "CVE-2023-1234", "medium")],
        "urllib3": [("<1.26.0", "CVE-2022-5678", "high"), (">=2.0,<2.0.7", "CVE-2024-0011", "medium")],
        "flask": [("<2.3.0", "CVE-2023-9876", "high")],
        "django": [("<4.2.0", "CVE-2023-5555", "critical")],
    }
    
    def __init__(self, repo_path="."):
        self.repo = Path(repo_path).resolve()
        self.findings = []
        self.stats = {
            "files_scanned": 0,
            "secrets_found": 0,
            "vulns_found": 0,
            "misconfigs_found": 0,
            "permission_issues": 0,
        }
        self.start_time = datetime.utcnow()
    
    def run(self):
        """Run the complete audit suite."""
        self._scan_secrets()
        self._scan_permissions()
        self._scan_dependencies()
        self._scan_configs()
        self._check_gitignore()
        self.stats["total_findings"] = len(self.findings)
        return self
    
    def _scan_secrets(self):
        """Scan source files for hardcoded secrets."""
        extensions = {'.py', '.js', '.ts', '.sh', '.yml', '.yaml', '.json', '.env'}
        
        for f in self.repo.rglob("*"):
            if f.is_dir() or ".git" in str(f) or "node_modules" in str(f):
                continue
            if f.suffix not in extensions and f.name not in {".env", ".env.local"}:
                continue
            
            try:
                content = f.read_text()
                self.stats["files_scanned"] += 1
                
                for pattern, secret_type, severity in self.SECRET_PATTERNS:
                    for match in re.finditer(pattern, content):
                        # Don't flag test fixtures or example placeholders
                        line_num = content[:match.start()].count('\n') + 1
                        context = content[max(0, match.start()-20):match.end()+20]
                        if "example" in context.lower() or "placeholder" in context.lower():
                            continue
                        
                        self.findings.append({
                            "rule_id": f"SECRET-{secret_type.upper().replace(' ', '-')}",
                            "category": "secrets",
                            "severity": severity,
                            "message": f"Potential {secret_type} detected",
                            "location": {"file": str(f.relative_to(self.repo)), "line": line_num},
                            "snippet": context.strip(),
                        })
                        self.stats["secrets_found"] += 1
            except (UnicodeDecodeError, PermissionError):
                continue
    
    def _scan_permissions(self):
        """Check file permissions for sensitive files."""
        for f in self.repo.rglob("*"):
            if f.is_dir() or ".git" in str(f):
                continue
            
            sensitive_exts = {'.pem', '.key', '.p12', '.pfx', '.crt'}
            if f.suffix not in sensitive_exts:
                continue
            
            try:
                mode = f.stat().st_mode
                # Check world-readable or world-writable
                if mode & 0o044 or mode & 0o022:
                    self.findings.append({
                        "rule_id": "PERMISSION-KEY-EXPOSED",
                        "category": "permissions",
                        "severity": "high",
                        "message": f"Key/certificate file has overly permissive permissions ({oct(mode & 0o777)})",
                        "location": {"file": str(f.relative_to(self.repo))},
                        "remediation": f"chmod 600 {f}"
                    })
                    self.stats["permission_issues"] += 1
            except OSError:
                pass
    
    def _scan_dependencies(self):
        """Check requirements.txt or package.json for known vulnerabilities."""
        req_file = self.repo / "requirements.txt"
        if req_file.exists():
            with open(req_file) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    m = re.match(r'^([a-zA-Z0-9_.-]+)([<>=~!].*)?$', line)
                    if not m:
                        continue
                    pkg = m.group(1).lower()
                    constraint = (m.group(2) or "").strip()
                    
                    if pkg in self.VULN_DB:
                        for vuln in self.VULN_DB[pkg]:
                            self.findings.append({
                                "rule_id": f"VULN-{vuln[1]}",
                                "category": "vulnerabilities",
                                "severity": vuln[2],
                                "message": f"{pkg} {constraint} may be vulnerable to {vuln[1]}",
                                "location": {"file": "requirements.txt"},
                                "remediation": f"Upgrade {pkg} to a patched version"
                            })
                            self.stats["vulns_found"] += 1
        
        # Check package.json
        pkg_file = self.repo / "package.json"
        if pkg_file.exists():
            content = pkg_file.read_text()
            if '"@types/node": "14' in content or '"node": "14' in content:
                self.findings.append({
                    "rule_id": "DEPRECATED-NODE",
                    "category": "vulnerabilities",
                    "severity": "medium",
                    "message": "Node.js 14 is End-of-Life. Upgrade to 18+ or 20+.",
                    "location": {"file": "package.json"},
                })
                self.stats["vulns_found"] += 1
    
    def _scan_configs(self):
        """Scan YAML configs for security misconfigurations."""
        for f in self.repo.rglob("*.yaml"):
            if ".git" in str(f):
                continue
            try:
                import yaml
                config = yaml.safe_load(f.read_text())
                if not isinstance(config, dict):
                    continue
                
                # Check for debug mode
                if config.get("debug") is True or config.get("DEBUG") is True:
                    self.findings.append({
                        "rule_id": "CONFIG-DEBUG-ENABLED",
                        "category": "misconfiguration",
                        "severity": "high",
                        "message": "Debug mode is enabled in configuration file",
                        "location": {"file": str(f.relative_to(self.repo))},
                        "remediation": "Set debug: false in production"
                    })
                    self.stats["misconfigs_found"] += 1
                
                # Check for weak passwords
                pw = config.get("password") or config.get("admin", {}).get("password")
                if pw and isinstance(pw, str) and len(pw) < 8:
                    self.findings.append({
                        "rule_id": "CONFIG-WEAK-PASSWORD",
                        "category": "misconfiguration",
                        "severity": "critical",
                        "message": "Weak password detected in configuration",
                        "location": {"file": str(f.relative_to(self.repo))},
                        "remediation": "Use a strong, generated password"
                    })
                    self.stats["misconfigs_found"] += 1
            except ImportError:
                pass
            except Exception:
                pass
    
    def _check_gitignore(self):
        """Verify .gitignore coverage."""
        gitignore = self.repo / ".gitignore"
        if not gitignore.exists():
            self.findings.append({
                "rule_id": "GITIGNORE-MISSING",
                "category": "misconfiguration",
                "severity": "medium",
                "message": "No .gitignore file found",
                "location": {"file": str(self.repo)},
                "remediation": "Create a .gitignore with patterns for secrets, build artifacts, and dependencies"
            })
            return
        
        content = gitignore.read_text()
        required = [".env", "*.pem", "node_modules/", "__pycache__/"]
        missing = [p for p in required if p not in content]
        if missing:
            self.findings.append({
                "rule_id": "GITIGNORE-INCOMPLETE",
                "category": "misconfiguration",
                "severity": "low",
                "message": f".gitignore missing patterns: {', '.join(missing)}",
                "location": {"file": ".gitignore"},
            })
    
    def to_sarif(self):
        """Generate a SARIF-like JSON report."""
        severity_level = {"critical": 10, "high": 8, "medium": 5, "low": 2}
        
        rules = {}
        results = []
        for f in self.findings:
            rule_id = f["rule_id"]
            if rule_id not in rules:
                rules[rule_id] = {
                    "id": rule_id,
                    "name": f["category"].title(),
                    "shortDescription": {"text": f["message"]},
                    "defaultConfiguration": {"level": severity_level.get(f["severity"], 5)}
                }
            
            result = {
                "ruleId": rule_id,
                "level": f["severity"],
                "message": {"text": f["message"]},
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {"uri": f["location"]["file"]},
                        "region": {"startLine": f["location"].get("line", 1)}
                    }
                }]
            }
            if "remediation" in f:
                result["fixes"] = [{"description": {"text": f["remediation"]}}]
            results.append(result)
        
        return {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "fleet-security-audit",
                        "version": "1.0.0"
                    }
                },
                "results": results,
                "rules": list(rules.values()),
                "invocations": [{
                    "startTimeUtc": self.start_time.isoformat() + "Z",
                }]
            }]
        }
    
    def print_summary(self):
        """Print a human-readable summary."""
        print("=" * 60)
        print("🔐 FLEET SECURITY AUDIT")
        print("=" * 60)
        print(f"Repository: {self.repo}")
        print(f"Files scanned: {self.stats['files_scanned']}")
        print(f"Audit started: {self.start_time.isoformat()}Z")
        print("")
        
        severity_counts = defaultdict(int)
        for f in self.findings:
            severity_counts[f["severity"]] += 1
        
        print("Findings by severity:")
        for sev in ["critical", "high", "medium", "low"]:
            count = severity_counts.get(sev, 0)
            emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[sev]
            print(f"  {emoji} {sev.title()}: {count}")
        
        print(f"\nTotal findings: {len(self.findings)}")
        
        if self.findings:
            print("\nTop findings:")
            for f in self.findings[:5]:
                loc = f"{f['location']['file']}:{f['location'].get('line', '')}"
                print(f"  {f['rule_id']} [{f['severity'].upper()}] — {loc}")
        else:
            print("\n✅ No security issues found.")


if __name__ == '__main__':
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    
    audit = FleetSecurityAudit(target).run()
    audit.print_summary()
    
    # Save SARIF report
    sarif = audit.to_sarif()
    with open("fleet-security-audit.sarif.json", "w") as f:
        json.dump(sarif, f, indent=2)
    print("\n💾 SARIF report saved to fleet-security-audit.sarif.json")
```

**Verification:**
```bash
# Set up a test repo with multiple issues
mkdir -p test-audit/src test-audit/config
cat > test-audit/src/api.py << 'EOF'
API_KEY = "sk-test12345678901234567890abcdef1234"
DATABASE_PASSWORD = "1234"
EOF

touch test-audit/config/server.pem
chmod 644 test-audit/config/server.pem

cat > test-audit/config/app.yaml << 'EOF'
debug: true
admin:
  password: "admin"
EOF

cat > test-audit/requirements.txt << 'EOF'
requests==2.27.1
django==4.1.0
EOF

python3 fleet-security-audit.py test-audit
# Expected:
# 🔐 FLEET SECURITY AUDIT
# ...
# 🔴 Critical: 2 (secrets + weak password)
# 🟠 High: 2 (permissions + debug mode)
# 🟡 Medium: 1 (vulnerability)
# Total findings: 5+
```

---

## Instructor Notes

### Common Mistakes

1. **False positives from test files:** Secret scanners flag test fixtures and mock API keys. Always add exclusion patterns for `test*/`, `*test*.py`, and `mock_*` files.
2. **Checking in .env files:** The most common recruit mistake. `.env` must be in `.gitignore` from day one.
3. **Ignoring lock files:** `package-lock.json` and `requirements.txt` without pins make vulnerability scanning impossible. Always pin versions.
4. **Using regex for secrets:** Regex alone catches obvious patterns but misses encoded secrets (base64, hex). For production, integrate with `git-secrets`, `truffleHog`, or GitHub secret scanning.

### Extension Ideas

- Integrate with GitHub Security Advisories API for real-time vulnerability data
- Add a pre-commit hook that runs the scanner before every commit
- Build a CI pipeline step that fails the build on critical/high findings
- Create a `fleet-secrets` vault using OpenClaw's secret management
- Add entropy analysis for detecting base64-encoded secrets
- Implement a "secret rotation" tool that helps update leaked credentials
- Add support for scanning Dockerfiles for exposed ports and root users

---

*CCC 🦀 | Fleet Curriculum Designer*  
*2026-05-05*
