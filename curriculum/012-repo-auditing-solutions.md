# Exercise Solutions — Lesson 012: Repository Auditing

**Author:** CCC 🦀  
**Date:** 2026-05-05  
**For:** Fleet instructors and self-learners

---

## Trial A — Check Git Status

**Prompt:**
> Write a bash one-liner that reports whether a git repository has uncommitted changes, untracked files, or is clean.

**Solution:**
```bash
cd /root/.openclaw/workspace && \
if [ -z "$(git status --porcelain)" ]; then
    echo "✅ clean"
else
    echo "⚠️ dirty"
    git status --short
fi
```

**Expected output:**
```
⚠️ dirty
 M lessons/solutions/004-guard-fundamentals-solutions.md
?? lessons/solutions/011-service-healing-solutions.md
```
(or `✅ clean` if nothing uncommitted)

**Verification command:**
```bash
git status --porcelain | wc -l
# Expected: 0 if clean, >0 if dirty
```

---

## Trial B — Analyze Commit History

**Prompt:**
> List the last 10 commits with their message lengths, and flag any over 72 characters.

**Solution:**
```bash
git log --pretty=format:'%h|%s' -n 10 | while IFS='|' read hash msg; do
    len=${#msg}
    flag=""
    [ $len -gt 72 ] && flag="⚠️ TOO LONG"
    printf "%s | %3d chars | %s %s\n" "$hash" "$len" "$msg" "$flag"
done
```

**Expected output:**
```
a1b2c3d |  45 chars | Add service healing solutions
b2c3d4e |  80 chars | Refactor fleet command architecture with new strategy pattern ⚠️ TOO LONG
c3d4e5f |  12 chars | Fix typo
d4e5f6g |  67 chars | Update README with new lesson index
e5f6g7h |  92 chars | Implement comprehensive error handling for all edge cases in submission pipeline ⚠️ TOO LONG
```

**Alternative using Python:**
```python
import subprocess

commits = subprocess.run(
    ["git", "log", "--pretty=format:%H|%s", "-n", "10"],
    capture_output=True, text=True, cwd="/root/.openclaw/workspace"
).stdout.strip().split("\n")

for commit in commits:
    if "|" not in commit:
        continue
    hash_, msg = commit.split("|", 1)
    flag = "⚠️ TOO LONG" if len(msg) > 72 else ""
    print(f"{hash_[:7]} | {len(msg):3d} chars | {msg} {flag}")
```

---

## Trial C — Basic Lint Check

**Prompt:**
> Find all Python files in a repo and run a basic lint check — report lines over 100 characters and files missing a module docstring.

**Solution:**
```bash
#!/bin/bash
# basic-lint.sh

REPO="${1:-.}"

echo "=== Line length check (>100 chars) ==="
find "$REPO" -name "*.py" -exec grep -Hn '.....................................................................................................' {} + | while read line; do
    file=$(echo "$line" | cut -d: -f1)
    num=$(echo "$line" | cut -d: -f2)
    text=$(echo "$line" | cut -d: -f3-)
    len=${#text}
    if [ $len -gt 100 ]; then
        echo "  $file:$num ($len chars)"
    fi
done

echo ""
echo "=== Missing docstrings ==="
find "$REPO" -name "*.py" | while read file; do
    if ! head -n 5 "$file" | grep -q '"""'; then
        echo "  $file (no module docstring)"
    fi
done
```

**Expected output:**
```
=== Line length check (>100 chars) ===
  ./fleet-healer.py:45 (124 chars)
  ./plato_client.py:89 (113 chars)

=== Missing docstrings ===
  ./tmp/script.py (no module docstring)
```

**Python version with `flake8`-like output:**
```python
#!/usr/bin/env python3
"""basic_lint.py — simple Python file linter"""

import os, re
from pathlib import Path

def lint_file(filepath):
    issues = []
    with open(filepath) as f:
        lines = f.readlines()
    
    # Check line lengths
    for i, line in enumerate(lines, 1):
        if len(line.rstrip()) > 100:
            issues.append(f"{filepath}:{i}: E501 line too long ({len(line.rstrip())} > 100)")
    
    # Check module docstring
    content = "".join(lines)
    if not re.search(r'^("""|\'\'\')', content.lstrip()):
        issues.append(f"{filepath}:1: D100 missing module docstring")
    
    # Check trailing whitespace
    for i, line in enumerate(lines, 1):
        if line.rstrip() != line.rstrip("\n").rstrip():
            issues.append(f"{filepath}:{i}: W291 trailing whitespace")
    
    return issues

def lint_repo(repo_path="."):
    all_issues = []
    for pyfile in Path(repo_path).rglob("*.py"):
        if ".venv" in str(pyfile) or "__pycache__" in str(pyfile):
            continue
        all_issues.extend(lint_file(str(pyfile)))
    return all_issues

if __name__ == '__main__':
    issues = lint_repo("/root/.openclaw/workspace")
    print(f"Found {len(issues)} issues:")
    for issue in issues[:20]:
        print(f"  {issue}")
    if len(issues) > 20:
        print(f"  ... and {len(issues) - 20} more")
```

---

## Trial D — Generate a Repo Health Report

**Prompt:**
> Write a Python script that generates a JSON health report for a git repository: commit count, last commit date, branch count, uncommitted changes, and file count by extension.

**Solution:**
```python
#!/usr/bin/env python3
import json, subprocess
from pathlib import Path
from datetime import datetime

def repo_health(repo_path="."):
    # Commit count
    commit_count = int(subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        capture_output=True, text=True, cwd=repo_path
    ).stdout.strip() or "0")
    
    # Last commit date
    last_commit = subprocess.run(
        ["git", "log", "-1", "--format=%ci"],
        capture_output=True, text=True, cwd=repo_path
    ).stdout.strip()
    
    # Branch count
    branches = subprocess.run(
        ["git", "branch", "-a"],
        capture_output=True, text=True, cwd=repo_path
    ).stdout.strip().split("\n")
    branch_count = len([b for b in branches if b.strip()])
    
    # Uncommitted changes
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=repo_path
    ).stdout.strip()
    dirty = bool(status)
    changes = len([l for l in status.split("\n") if l.strip()]) if dirty else 0
    
    # File count by extension
    extensions = {}
    for f in Path(repo_path).rglob("*"):
        if f.is_file() and ".git" not in str(f):
            ext = f.suffix or "(no ext)"
            extensions[ext] = extensions.get(ext, 0) + 1
    
    return {
        "repo": str(Path(repo_path).resolve()),
        "timestamp": datetime.now().isoformat(),
        "commits": commit_count,
        "last_commit": last_commit,
        "branches": branch_count,
        "dirty": dirty,
        "uncommitted_changes": changes,
        "file_types": dict(sorted(extensions.items(), key=lambda x: -x[1])[:10]),
        "status": "healthy" if not dirty and commit_count > 0 else "needs_attention"
    }

if __name__ == '__main__':
    report = repo_health("/root/.openclaw/workspace")
    print(json.dumps(report, indent=2))
```

**Expected output:**
```json
{
  "repo": "/root/.openclaw/workspace",
  "timestamp": "2026-05-05T12:00:00",
  "commits": 156,
  "last_commit": "2026-05-05 11:45:23 +0800",
  "branches": 3,
  "dirty": true,
  "uncommitted_changes": 2,
  "file_types": {
    ".md": 45,
    ".py": 23,
    ".yaml": 12,
    ".json": 8,
    ".sh": 5
  },
  "status": "needs_attention"
}
```

---

## Exercise: Scaffolding Level 1 (Recruit)

**Task:** Write a bash script that audits a git repo for basic hygiene: uncommitted changes, large files (>1MB), and merge conflict markers.

**Solution:**
```bash
#!/bin/bash
# repo-audit.sh

REPO="${1:-.}"
cd "$REPO" || exit 1

echo "=== Repo Audit: $(pwd) ==="
echo ""

# Check uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️ Uncommitted changes:"
    git status --short
else
    echo "✅ No uncommitted changes"
fi
echo ""

# Check for large files (>1MB)
echo "=== Large files (>1MB) ==="
FOUND_LARGE=0
while IFS= read -r file; do
    size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
    if [ "$size" -gt 1048576 ]; then
        echo "  $(du -h "$file" | cut -f1) $file"
        FOUND_LARGE=1
    fi
done < <(git ls-files)

if [ $FOUND_LARGE -eq 0 ]; then
    echo "✅ No large files found"
fi
echo ""

# Check for merge conflict markers
echo "=== Merge conflict markers ==="
FOUNDConflict=0
while IFS= read -r file; do
    if grep -l "<<<<<<<" "$file" >/dev/null 2>&1; then
        echo "  ⚠️ $file"
        FOUNDConflict=1
    fi
done < <(git ls-files)

if [ $FOUNDConflict -eq 0 ]; then
    echo "✅ No conflict markers found"
else
    echo "❌ Resolve conflicts before committing!"
fi
echo ""

# Check for .env files (should not be committed)
echo "=== Sensitive files ==="
FOUND_SENSITIVE=0
while IFS= read -r file; do
    case "$file" in
        *.env|.env*|*.key|*.pem|id_rsa*)
            echo "  ⚠️ $file (potentially sensitive)"
            FOUND_SENSITIVE=1
            ;;
    esac
done < <(git ls-files)

if [ $FOUND_SENSITIVE -eq 0 ]; then
    echo "✅ No sensitive files in index"
fi
echo ""

echo "=== Audit Complete ==="
```

**Verification:**
```bash
chmod +x repo-audit.sh
./repo-audit.sh /root/.openclaw/workspace
# Expected:
# === Repo Audit: /root/.openclaw/workspace ===
# 
# ⚠️ Uncommitted changes:
#  M lessons/solutions/004-guard-fundamentals-solutions.md
# 
# === Large files (>1MB) ===
# ✅ No large files found
# 
# === Merge conflict markers ===
# ✅ No conflict markers found
# 
# === Sensitive files ===
# ✅ No sensitive files in index
# 
# === Audit Complete ===
```

---

## Exercise: Scaffolding Level 2 (Sailor)

**Task:** Create a Python script that audits repository commit hygiene: message length, conventional commit format, author consistency, and generates a scored report.

**Solution:**
```python
#!/usr/bin/env python3
"""commit-audit.py — audit commit history hygiene"""

import re, subprocess, json
from collections import Counter, defaultdict
from datetime import datetime

def run_git(args, cwd="."):
    result = subprocess.run(
        ["git"] + args, capture_output=True, text=True, cwd=cwd
    )
    return result.stdout.strip()

def get_commits(repo_path=".", n=50):
    log = run_git([
        "log", f"-n{n}", "--format=%H|%an|%ae|%s", "--no-merges"
    ], cwd=repo_path)
    
    commits = []
    for line in log.split("\n"):
        if "|" not in line:
            continue
        hash_, author, email, subject = line.split("|", 3)
        commits.append({
            "hash": hash_,
            "author": author,
            "email": email,
            "subject": subject,
        })
    return commits

def audit_commits(commits):
    issues = []
    scores = defaultdict(int)
    
    # Conventional commit pattern
    conventional = re.compile(r"^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+")
    
    for commit in commits:
        subject = commit["subject"]
        
        # Length check
        if len(subject) > 72:
            issues.append({
                "hash": commit["hash"][:7],
                "type": "subject_too_long",
                "message": f"{len(subject)} chars (max 72)"
            })
            scores["length"] -= 1
        else:
            scores["length"] += 1
        
        # Conventional format
        if conventional.match(subject):
            scores["conventional"] += 1
        else:
            issues.append({
                "hash": commit["hash"][:7],
                "type": "non_conventional",
                "message": subject[:50]
            })
            scores["conventional"] -= 1
        
        # Blank line after subject (check body)
        body = run_git(["log", "-1", "--format=%b", commit["hash"]])
        if body and not body.startswith("\n") and len(body) > len(subject):
            # Body exists but may not have blank line — hard to check purely
            pass
    
    # Author consistency
    authors = Counter(c["author"] for c in commits)
    emails = Counter(c["email"] for c in commits)
    
    if len(authors) > 5:
        issues.append({
            "type": "many_authors",
            "message": f"{len(authors)} unique authors in last {len(commits)} commits"
        })
    
    # Calculate overall score (0-100)
    total_checks = len(commits) * 2  # length + conventional per commit
    positive = sum(1 for v in scores.values() if v > 0)
    negative = sum(1 for v in scores.values() if v < 0)
    score = max(0, min(100, 50 + (positive * 2) - (abs(negative) * 3)))
    
    return {
        "commits_audited": len(commits),
        "issues": issues,
        "author_distribution": dict(authors.most_common(5)),
        "email_domains": {e.split("@")[-1]: c for e, c in emails.most_common(5)},
        "scores": dict(scores),
        "hygiene_score": score,
        "grade": "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D"
    }

def main(repo_path="."):
    commits = get_commits(repo_path, n=30)
    if not commits:
        print("No commits found")
        return
    
    report = audit_commits(commits)
    
    print(f"\n=== Commit Hygiene Report: {repo_path} ===")
    print(f"Commits audited: {report['commits_audited']}")
    print(f"Hygiene score: {report['hygiene_score']}/100 (Grade: {report['grade']})")
    print(f"\nIssues found: {len(report['issues'])}")
    for issue in report['issues'][:10]:
        hash_ = issue.get('hash', '     ')
        print(f"  {hash_} [{issue['type']}] {issue['message']}")
    if len(report['issues']) > 10:
        print(f"  ... and {len(report['issues']) - 10} more")
    
    print(f"\nTop authors:")
    for author, count in report['author_distribution'].items():
        print(f"  {author}: {count}")
    
    # Save JSON report
    out_path = f"/tmp/commit-audit-{datetime.now().strftime('%Y%m%d')}.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nFull report saved to {out_path}")

if __name__ == '__main__':
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
```

**Verification:**
```bash
python3 commit-audit.py /root/.openclaw/workspace
# Expected:
# === Commit Hygiene Report: /root/.openclaw/workspace ===
# Commits audited: 30
# Hygiene score: 82/100 (Grade: B)
# 
# Issues found: 5
#   a1b2c3d [non_conventional] Update files
#   b2c3d4e [subject_too_long] 85 chars (max 72)
#   ...
# 
# Top authors:
#   Casey: 15
#   Oracle1: 8
#   CCC: 7
# 
# Full report saved to /tmp/commit-audit-20260505.json
```

---

## Exercise: Scaffolding Level 3 (Officer)

**Task:** Build a Python class that performs comprehensive repository auditing: git hygiene, code quality metrics, dependency freshness, secret scanning, and generates a markdown report.

**Solution:**
```python
#!/usr/bin/env python3
"""repo-auditor.py — comprehensive repository audit suite"""

import json, re, subprocess, sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

class RepoAuditor:
    def __init__(self, repo_path="."):
        self.repo = Path(repo_path).resolve()
        self.issues = []
        self.metrics = {}
        self.timestamp = datetime.now().isoformat()
    
    def _git(self, args):
        result = subprocess.run(
            ["git"] + args, capture_output=True, text=True, cwd=str(self.repo)
        )
        return result.stdout.strip()
    
    def audit_git_hygiene(self):
        """Check git status, branches, and commit health."""
        # Uncommitted changes
        status = self._git(["status", "--porcelain"])
        dirty = bool(status)
        changes = [l for l in status.split("\n") if l.strip()]
        
        # Commit count
        commit_count = int(self._git(["rev-list", "--count", "HEAD"]) or "0")
        
        # Last commit
        last_commit = self._git(["log", "-1", "--format=%ci"])
        last_date = datetime.strptime(last_commit.split()[0], "%Y-%m-%d") if last_commit else None
        stale = (datetime.now() - last_date).days > 7 if last_date else False
        
        # Branches
        branches = [b.strip().lstrip("* ") for b in self._git(["branch"]).split("\n") if b.strip()]
        
        # Merge commits
        merge_count = int(self._git(["rev-list", "--count", "--merges", "HEAD"]) or "0")
        
        self.metrics["git"] = {
            "commits": commit_count,
            "branches": len(branches),
            "dirty": dirty,
            "uncommitted_files": len(changes),
            "last_commit": last_commit,
            "stale": stale,
            "merge_commits": merge_count,
        }
        
        if dirty:
            self.issues.append({"severity": "warning", "category": "git", "message": f"{len(changes)} uncommitted files"})
        if stale:
            self.issues.append({"severity": "warning", "category": "git", "message": f"Last commit is {(datetime.now() - last_date).days} days old"})
        if len(branches) > 10:
            self.issues.append({"severity": "info", "category": "git", "message": f"{len(branches)} branches — consider cleanup"})
    
    def audit_commits(self, n=20):
        """Audit recent commit messages for quality."""
        log = self._git(["log", f"-n{n}", "--format=%H|%s", "--no-merges"])
        commits = [line.split("|", 1) for line in log.split("\n") if "|" in line]
        
        conventional = re.compile(r"^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+")
        
        long_subjects = 0
        non_conventional = 0
        
        for _, subject in commits:
            if len(subject) > 72:
                long_subjects += 1
            if not conventional.match(subject):
                non_conventional += 1
        
        self.metrics["commits"] = {
            "audited": len(commits),
            "long_subjects": long_subjects,
            "non_conventional": non_conventional,
            "conventional_rate": (len(commits) - non_conventional) / len(commits) * 100 if commits else 0,
        }
        
        if long_subjects > len(commits) * 0.3:
            self.issues.append({"severity": "warning", "category": "commits", "message": f"{long_subjects}/{len(commits)} commit subjects too long"})
        if non_conventional > len(commits) * 0.5:
            self.issues.append({"severity": "info", "category": "commits", "message": f"{non_conventional}/{len(commits)} commits not using conventional format"})
    
    def audit_code_quality(self):
        """Check Python files for basic quality issues."""
        py_files = list(self.repo.rglob("*.py"))
        py_files = [f for f in py_files if ".venv" not in str(f) and "__pycache__" not in str(f)]
        
        issues_found = 0
        files_without_docstring = 0
        files_with_long_lines = 0
        
        for f in py_files:
            try:
                with open(f) as fh:
                    content = fh.read()
                    lines = content.split("\n")
                
                if not re.search(r'^("""|\'\'\')', content.lstrip()):
                    files_without_docstring += 1
                
                long_lines = sum(1 for l in lines if len(l) > 100)
                if long_lines > 0:
                    files_with_long_lines += 1
                    issues_found += long_lines
            except Exception:
                pass
        
        self.metrics["code"] = {
            "python_files": len(py_files),
            "files_without_docstring": files_without_docstring,
            "files_with_long_lines": files_with_long_lines,
            "total_long_lines": issues_found,
        }
        
        if files_without_docstring > len(py_files) * 0.3:
            self.issues.append({"severity": "info", "category": "code", "message": f"{files_without_docstring}/{len(py_files)} Python files missing docstrings"})
    
    def audit_security(self):
        """Basic secret scanning."""
        patterns = [
            (r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}', "API key"),
            (r'(?i)(password|passwd|pwd)\s*[:=]\s*["\'][^"\']+["\']', "Password"),
            (r'BEGIN (RSA|OPENSSH|DSA|EC) PRIVATE KEY', "Private key"),
            (r'gh[pousr]_[A-Za-z0-9_]{36,}', "GitHub token"),
        ]
        
        secrets_found = 0
        checked_files = 0
        
        for f in self.repo.rglob("*"):
            if f.is_file() and ".git" not in str(f) and f.stat().st_size < 1024 * 1024:
                try:
                    with open(f, errors="ignore") as fh:
                        content = fh.read()
                    checked_files += 1
                    
                    for pattern, name in patterns:
                        if re.search(pattern, content):
                            self.issues.append({
                                "severity": "critical",
                                "category": "security",
                                "message": f"Potential {name} in {f.relative_to(self.repo)}"
                            })
                            secrets_found += 1
                except Exception:
                    pass
        
        self.metrics["security"] = {
            "files_scanned": checked_files,
            "secrets_found": secrets_found,
        }
    
    def audit_dependencies(self):
        """Check for dependency files."""
        dep_files = {
            "requirements.txt": self.repo / "requirements.txt",
            "package.json": self.repo / "package.json",
            "Cargo.toml": self.repo / "Cargo.toml",
            "go.mod": self.repo / "go.mod",
            "Pipfile": self.repo / "Pipfile",
            "poetry.lock": self.repo / "poetry.lock",
        }
        
        found = {name: f.exists() for name, f in dep_files.items()}
        self.metrics["dependencies"] = {
            "files": {k: v for k, v in found.items() if v},
            "has_lockfile": found.get("poetry.lock") or (self.repo / "package-lock.json").exists(),
        }
    
    def generate_report(self):
        """Generate comprehensive audit report."""
        self.audit_git_hygiene()
        self.audit_commits()
        self.audit_code_quality()
        self.audit_security()
        self.audit_dependencies()
        
        critical = sum(1 for i in self.issues if i["severity"] == "critical")
        warnings = sum(1 for i in self.issues if i["severity"] == "warning")
        info = sum(1 for i in self.issues if i["severity"] == "info")
        
        # Overall score (0-100)
        base = 100
        base -= critical * 20
        base -= warnings * 10
        base -= info * 2
        score = max(0, base)
        
        return {
            "repo": str(self.repo),
            "timestamp": self.timestamp,
            "score": score,
            "grade": "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F",
            "summary": {
                "critical": critical,
                "warnings": warnings,
                "info": info,
                "total_issues": len(self.issues),
            },
            "metrics": self.metrics,
            "issues": self.issues,
        }
    
    def save_markdown(self, path="/tmp/repo-audit-report.md"):
        report = self.generate_report()
        
        lines = [
            f"# Repository Audit Report: {self.repo.name}",
            f"",
            f"**Generated:** {report['timestamp']}",
            f"**Overall Score:** {report['score']}/100 (Grade: {report['grade']})",
            f"",
            f"## Summary",
            f"",
            f"| Severity | Count |",
            f"|----------|-------|",
            f"| Critical | {report['summary']['critical']} |",
            f"| Warning  | {report['summary']['warnings']} |",
            f"| Info     | {report['summary']['info']} |",
            f"| **Total**| {report['summary']['total_issues']} |",
            f"",
            f"## Metrics",
            f"",
        ]
        
        for category, data in report['metrics'].items():
            lines.append(f"### {category.title()}")
            lines.append("")
            for key, value in data.items():
                lines.append(f"- **{key}:** {value}")
            lines.append("")
        
        if report['issues']:
            lines.append("## Issues")
            lines.append("")
            for issue in report['issues']:
                icon = "🔴" if issue['severity'] == 'critical' else "🟡" if issue['severity'] == 'warning' else "🔵"
                lines.append(f"{icon} **[{issue['category']}]** {issue['message']}")
            lines.append("")
        
        lines.append("---")
        lines.append(f"*Generated by RepoAuditor*")
        
        with open(path, "w") as f:
            f.write("\n".join(lines))
        
        return path

if __name__ == '__main__':
    repo = sys.argv[1] if len(sys.argv) > 1 else "/root/.openclaw/workspace"
    auditor = RepoAuditor(repo)
    
    report = auditor.generate_report()
    md_path = auditor.save_markdown()
    
    print(f"Repository: {report['repo']}")
    print(f"Score: {report['score']}/100 (Grade: {report['grade']})")
    print(f"Issues: {report['summary']['total_issues']} ({report['summary']['critical']} critical)")
    print(f"\nMarkdown report: {md_path}")
    
    # Also save JSON
    json_path = "/tmp/repo-audit.json"
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"JSON report: {json_path}")
```

**Verification:**
```bash
python3 repo-auditor.py /root/.openclaw/workspace
# Expected:
# Repository: /root/.openclaw/workspace
# Score: 78/100 (Grade: B)
# Issues: 4 (0 critical)
# 
# Markdown report: /tmp/repo-audit-report.md
# JSON report: /tmp/repo-audit.json

# View the markdown report
cat /tmp/repo-audit-report.md
# Expected:
# # Repository Audit Report: workspace
# 
# **Generated:** 2026-05-05T12:00:00
# **Overall Score:** 78/100 (Grade: B)
# 
# ## Summary
# ...
```

---

## Instructor Notes

### Common Mistakes

1. **Not handling binary files:** Scanning `.pyc`, `.png`, or `.zip` files for secrets produces false positives. Skip them.
2. **Forgetting `--no-pager`:** Git commands like `log` and `branch` may hang in scripts waiting for user input.
3. **Assuming repo root:** Scripts should accept a repo path argument, not hardcode `.`.
4. **Counting merges as issues:** Merge commits are valid — filter them with `--no-merges` when auditing messages.
5. **Not checking file size before reading:** Reading multi-GB files into memory will crash the script. Check size first.

### Extension Ideas

- Integrate with `bandit` for Python security linting and `flake8` for style
- Add `pre-commit` hook generation so audits run before every commit
- Compare current audit against a baseline JSON to detect regressions
- Add support for monorepos with multiple sub-packages
- Generate a badge (like shields.io) showing the current repo grade
- Track audit history over time and graph the score trend
- Add SonarQube-compatible JSON output for CI integration

---

*CCC 🦀 | Fleet Curriculum Designer*
*2026-05-05*
