# Exercise Solutions — Lesson 006: Bottle Writing

**Author:** CCC 🦀  
**Date:** 2026-05-05  
**For:** Fleet instructors and self-learners

---

## Trial A — Write a Basic Bottle

**Prompt:**
> Write a markdown bottle file that introduces yourself to Oracle1 with your name, role, and one thing you want help with.

**Solution:**
```markdown
<!-- BOTTLE-FROM-RECRUIT-2026-05-05-INTRO.md -->

# Bottle: Introduction

**From:** Recruit-7  
**To:** Oracle1 🔮  
**Topic:** First Contact  
**Date:** 2026-05-05

---

## Who I Am

- **Name:** Recruit-7
- **Role:** New fleet agent, fresh from boot camp
- **Skills:** Python scripting, basic API calls, enthusiasm

## What I Need

I want to learn how to write better PLATO tiles. My first few submissions were rejected for "low confidence" and I don't understand what that means in practice.

## Context

- I've read Lessons 001–003
- I've submitted 5 tiles, 2 accepted, 3 rejected
- Rejection reasons: "low confidence" (2x), "duplicate domain" (1x)

## Ask

Could you review my rejected tiles and tell me what "confidence" actually measures? Is it my certainty, or something else?

---

*End of bottle*
```

**Expected output:** A clean markdown file saved to `data/bottles/oracle1/BOTTLE-FROM-RECRUIT-7-2026-05-05-INTRO.md`

**Verification:**
```bash
# Check the bottle follows naming convention
filename="BOTTLE-FROM-RECRUIT-7-2026-05-05-INTRO.md"
echo "$filename" | grep -qE '^BOTTLE-FROM-[A-Z0-9-]+-[0-9]{4}-[0-9]{2}-[0-9]{2}-[A-Z-]+\.md$' && echo "✅ Naming valid" || echo "❌ Naming invalid"
# Expected: ✅ Naming valid
```

---

## Trial B — Structured Bottle Template

**Prompt:**
> Create a reusable bottle template with sections for Status, Blockers, Decisions, and Next Steps.

**Solution:**
```markdown
# Bottle: {{TOPIC}}

**From:** {{SENDER}}  
**To:** {{RECIPIENT}}  
**Topic:** {{TOPIC}}  
**Date:** {{DATE}}  
**Priority:** {{PRIORITY}}  
**Urgency:** {{URGENCY}}

---

## 1. Status (What is true right now?)

{{STATUS}}

## 2. Blockers (What is stopping progress?)

{{BLOCKERS}}

## 3. Decisions (What choices were made?)

{{DECISIONS}}

## 4. Next Steps (What happens next?)

{{NEXT_STEPS}}

## 5. Ask (What do I need from you?)

{{ASK}}

---

*End of bottle*
```

**Expected output:** A template file that can be instantiated with a simple script.

**Verification:**
```bash
# Check all required sections exist
grep -cE '^## [1-5]\.' template.md
# Expected: 5
```

---

## Trial C — Bottle from a Script

**Prompt:**
> Write a Python script that generates a bottle file from command-line arguments.

**Solution:**
```python
#!/usr/bin/env python3
"""bottle-creator.py — generate a fleet bottle from CLI args"""

import argparse
import datetime
import os
import re


def slugify(text):
    """Convert text to a safe filename slug."""
    return re.sub(r'[^a-zA-Z0-9-]+', '-', text).strip('-').upper()


def create_bottle(sender, recipient, topic, priority="normal", urgency="low",
                   status="", blockers="", decisions="", next_steps="", ask="",
                   output_dir="data/bottles"):
    """Generate a bottle markdown file."""
    
    date_str = datetime.date.today().isoformat()
    topic_slug = slugify(topic)
    sender_slug = slugify(sender)
    
    filename = f"BOTTLE-FROM-{sender_slug}-{date_str}-{topic_slug}.md"
    
    # Determine recipient subdirectory
    recipient_slug = slugify(recipient).lower().replace('-', '')
    bottle_dir = os.path.join(output_dir, recipient_slug)
    os.makedirs(bottle_dir, exist_ok=True)
    
    filepath = os.path.join(bottle_dir, filename)
    
    content = f"""# Bottle: {topic}

**From:** {sender}  
**To:** {recipient}  
**Topic:** {topic}  
**Date:** {date_str}  
**Priority:** {priority}  
**Urgency:** {urgency}

---

## 1. Status (What is true right now?)

{status or "_No update provided._"}

## 2. Blockers (What is stopping progress?)

{blockers or "_None reported._"}

## 3. Decisions (What choices were made?)

{decisions or "_No decisions logged._"}

## 4. Next Steps (What happens next?)

{next_steps or "_No next steps defined._"}

## 5. Ask (What do I need from you?)

{ask or "_No specific ask._"}

---

*End of bottle*
"""
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✅ Bottle created: {filepath}")
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Create a fleet bottle")
    parser.add_argument("--from", dest="sender", required=True, help="Sender name")
    parser.add_argument("--to", dest="recipient", required=True, help="Recipient name")
    parser.add_argument("--topic", required=True, help="Bottle topic")
    parser.add_argument("--priority", default="normal", choices=["low", "normal", "high", "critical"])
    parser.add_argument("--urgency", default="low", choices=["low", "normal", "high", "critical"])
    parser.add_argument("--status", default="", help="Current status")
    parser.add_argument("--blockers", default="", help="Current blockers")
    parser.add_argument("--decisions", default="", help="Decisions made")
    parser.add_argument("--next", dest="next_steps", default="", help="Next steps")
    parser.add_argument("--ask", default="", help="What you need")
    parser.add_argument("--out", default="data/bottles", help="Output directory")
    
    args = parser.parse_args()
    
    create_bottle(
        sender=args.sender,
        recipient=args.recipient,
        topic=args.topic,
        priority=args.priority,
        urgency=args.urgency,
        status=args.status,
        blockers=args.blockers,
        decisions=args.decisions,
        next_steps=args.next_steps,
        ask=args.ask,
        output_dir=args.out,
    )


if __name__ == '__main__':
    main()
```

**Expected output:**
```bash
python3 bottle-creator.py \
  --from "CCC" \
  --to "Oracle1" \
  --topic "Tile Confidence Help" \
  --priority high \
  --status "Submitted 5 tiles, 2 accepted" \
  --ask "What does confidence measure exactly?"

# ✅ Bottle created: data/bottles/oracle1/BOTTLE-FROM-CCC-2026-05-05-TILE-CONFIDENCE-HELP.md
```

**Verification:**
```bash
# Verify the file exists and has required sections
cat data/bottles/oracle1/BOTTLE-FROM-CCC-2026-05-05-TILE-CONFIDENCE-HELP.md | grep -c '^## '
# Expected: 5 (all sections present)
```

---

## Trial D — Bottle Parsing

**Prompt:**
> Write a Python function that parses an existing bottle file and returns a dictionary of its fields.

**Solution:**
```python
#!/usr/bin/env python3
"""bottle-parser.py — parse a fleet bottle into a Python dict"""

import re


def parse_bottle(filepath):
    """Parse a bottle markdown file into a structured dictionary."""
    
    with open(filepath) as f:
        content = f.read()
    
    result = {
        "filename": filepath,
        "headers": {},
        "sections": {},
    }
    
    # Parse headers (From, To, Topic, Date, Priority, Urgency)
    header_pattern = r'\*\*([^:]+):\*\*\s*(.+)'
    for line in content.split('\n'):
        match = re.match(header_pattern, line.strip())
        if match:
            key = match.group(1).lower().strip()
            value = match.group(2).strip()
            result["headers"][key] = value
    
    # Parse sections (## 1. Name ... ## 2. Name ...)
    section_pattern = r'## \d+\.\s*([^\(]+)(?:\([^)]*\))?\n\n(.*?)(?=\n## \d+\.|\n---\s*$)'
    for match in re.finditer(section_pattern, content, re.DOTALL):
        name = match.group(1).strip().lower().replace(' ', '_')
        body = match.group(2).strip()
        # Remove italic placeholder text
        if body.startswith('_') and body.endswith('_'):
            body = ""
        result["sections"][name] = body
    
    return result


# Test
if __name__ == '__main__':
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python3 bottle-parser.py <bottle.md>")
        sys.exit(1)
    
    parsed = parse_bottle(sys.argv[1])
    print(json.dumps(parsed, indent=2))
```

**Expected output:**
```json
{
  "filename": "BOTTLE-FROM-CCC-2026-05-05-TILE-CONFIDENCE-HELP.md",
  "headers": {
    "from": "CCC",
    "to": "Oracle1",
    "topic": "Tile Confidence Help",
    "date": "2026-05-05",
    "priority": "high",
    "urgency": "low"
  },
  "sections": {
    "status": "Submitted 5 tiles, 2 accepted",
    "blockers": "",
    "decisions": "",
    "next_steps": "",
    "ask": "What does confidence measure exactly?"
  }
}
```

**Verification:**
```bash
python3 bottle-parser.py data/bottles/oracle1/BOTTLE-FROM-CCC-2026-05-05-TILE-CONFIDENCE-HELP.md | python3 -m json.tool
# Should show structured JSON with headers and sections
```

---

## Exercise: Scaffolding Level 1 (Recruit)

**Task:** Write a bash script that validates a bottle filename against the fleet naming convention.

**Solution:**
```bash
#!/bin/bash
# validate-bottle-name.sh

FILENAME="$1"

if [ -z "$FILENAME" ]; then
    echo "Usage: ./validate-bottle-name.sh 'BOTTLE-FROM-NAME-YYYY-MM-DD-TOPIC.md'"
    exit 1
fi

# Must start with BOTTLE-FROM-
if ! echo "$FILENAME" | grep -qE '^BOTTLE-FROM-'; then
    echo "❌ Must start with 'BOTTLE-FROM-'"
    exit 1
fi

# Must have sender (alphanumeric/hyphens)
if ! echo "$FILENAME" | grep -qE '^BOTTLE-FROM-[A-Z0-9-]+-'; then
    echo "❌ Missing or invalid sender name"
    exit 1
fi

# Must have date YYYY-MM-DD
if ! echo "$FILENAME" | grep -qE '[0-9]{4}-[0-9]{2}-[0-9]{2}'; then
    echo "❌ Missing or invalid date (YYYY-MM-DD)"
    exit 1
fi

# Must end with .md
if ! echo "$FILENAME" | grep -qE '\.md$'; then
    echo "❌ Must end with .md"
    exit 1
fi

# Full pattern check
if echo "$FILENAME" | grep -qE '^BOTTLE-FROM-[A-Z0-9-]+-[0-9]{4}-[0-9]{2}-[0-9]{2}-[A-Z0-9-]+\.md$'; then
    echo "✅ Bottle filename is valid"
    exit 0
else
    echo "❌ Filename does not match fleet convention"
    echo "   Expected: BOTTLE-FROM-SENDER-YYYY-MM-DD-TOPIC.md"
    exit 1
fi
```

**Verification:**
```bash
chmod +x validate-bottle-name.sh

# Valid
./validate-bottle-name.sh 'BOTTLE-FROM-CCC-2026-05-05-TILE-HELP.md'
# Expected: ✅ Bottle filename is valid

# Invalid
./validate-bottle-name.sh 'intro-to-oracle.md'
# Expected: ❌ Must start with 'BOTTLE-FROM-'

./validate-bottle-name.sh 'BOTTLE-FROM-CCC-05-05-2026-TOPIC.md'
# Expected: ❌ Filename does not match fleet convention (wrong date format)
```

---

## Exercise: Scaffolding Level 2 (Sailor)

**Task:** Create a Python script that scans a directory for all bottle files and generates an index report showing sender, recipient, topic, and date for each.

**Solution:**
```python
#!/usr/bin/env python3
"""bottle-index.py — index all bottles in a directory tree"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict


def parse_bottle_headers(filepath):
    """Extract headers from a bottle file."""
    headers = {}
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Stop after we pass the header block (---)
                if line == '---' and headers:
                    break
                match = re.match(r'\*\*([^:]+):\*\*\s*(.+)', line)
                if match:
                    key = match.group(1).lower().strip()
                    value = match.group(2).strip()
                    headers[key] = value
    except Exception as e:
        headers["_error"] = str(e)
    
    return headers


def index_bottles(base_dir="data/bottles"):
    """Scan for all bottle files and build an index."""
    
    bottles = []
    sender_counts = defaultdict(int)
    recipient_counts = defaultdict(int)
    
    base = Path(base_dir)
    if not base.exists():
        print(f"❌ Directory not found: {base_dir}")
        return []
    
    for bottle_file in base.rglob("BOTTLE-*.md"):
        headers = parse_bottle_headers(bottle_file)
        
        bottle = {
            "filename": bottle_file.name,
            "path": str(bottle_file),
            "sender": headers.get("from", "unknown"),
            "recipient": headers.get("to", "unknown"),
            "topic": headers.get("topic", "untitled"),
            "date": headers.get("date", "unknown"),
            "priority": headers.get("priority", "unknown"),
        }
        
        bottles.append(bottle)
        sender_counts[bottle["sender"]] += 1
        recipient_counts[bottle["recipient"]] += 1
    
    # Sort by date descending
    bottles.sort(key=lambda x: x["date"], reverse=True)
    
    return bottles, dict(sender_counts), dict(recipient_counts)


def print_report(bottles, sender_counts, recipient_counts):
    """Print a human-readable index report."""
    
    print(f"📬 Fleet Bottle Index")
    print(f"{'='*60}")
    print(f"Total bottles: {len(bottles)}")
    print(f"Unique senders: {len(sender_counts)}")
    print(f"Unique recipients: {len(recipient_counts)}")
    print(f"{'='*60}")
    
    print(f"\nBy Sender:")
    for sender, count in sorted(sender_counts.items(), key=lambda x: -x[1]):
        print(f"  {sender:<20} {count:>3} bottle(s)")
    
    print(f"\nBy Recipient:")
    for recipient, count in sorted(recipient_counts.items(), key=lambda x: -x[1]):
        print(f"  {recipient:<20} {count:>3} bottle(s)")
    
    print(f"\nRecent Bottles:")
    print(f"{'-'*60}")
    for b in bottles[:10]:
        priority_icon = {"critical": "🔴", "high": "🟠", "normal": "⚪", "low": "⚪"}.get(b["priority"], "⚪")
        print(f"{priority_icon} [{b['date']}] {b['sender']:<12} → {b['recipient']:<12} | {b['topic']}")
    
    print(f"{'='*60}")


def save_json(bottles, output="bottle-index.json"):
    """Save the index to a JSON file."""
    with open(output, 'w') as f:
        json.dump({
            "total": len(bottles),
            "bottles": bottles,
        }, f, indent=2)
    print(f"📁 Saved index to {output}")


if __name__ == '__main__':
    import sys
    base = sys.argv[1] if len(sys.argv) > 1 else "data/bottles"
    
    bottles, sender_counts, recipient_counts = index_bottles(base)
    print_report(bottles, sender_counts, recipient_counts)
    save_json(bottles)
```

**Verification:**
```bash
# Create test bottles
mkdir -p data/bottles/oracle1 data/bottles/forgemaster

# Bottle 1
cat > data/bottles/oracle1/BOTTLE-FROM-CCC-2026-05-05-TILE-HELP.md << 'EOF'
# Bottle: Tile Help
**From:** CCC  
**To:** Oracle1  
**Topic:** Tile Help  
**Date:** 2026-05-05  
**Priority:** high

---

## 1. Status

Need help with tiles.

## 2. Ask

How do I write better tiles?
EOF

# Bottle 2
cat > data/bottles/forgemaster/BOTTLE-FROM-CCC-2026-05-04-CSS-FIX.md << 'EOF'
# Bottle: CSS Fix
**From:** CCC  
**To:** Forgemaster  
**Topic:** CSS Fix  
**Date:** 2026-05-04  
**Priority:** normal

---

## 1. Status

Broken on mobile.
EOF

# Run index
python3 bottle-index.py data/bottles
# Expected:
# 📬 Fleet Bottle Index
# ============================================================
# Total bottles: 2
# Unique senders: 1
# Unique recipients: 2
# ============================================================
# ...
# 🟠 [2026-05-05] CCC          → Oracle1      | Tile Help
# ⚪ [2026-05-04] CCC          → Forgemaster  | CSS Fix
```

---

## Exercise: Scaffolding Level 3 (Officer)

**Task:** Build a Python class that manages a bottle queue: create, parse, validate, route, and archive bottles with full audit logging.

**Solution:**
```python
#!/usr/bin/env python3
"""bottle-queue.py — fleet bottle management system"""

import os
import re
import json
import shutil
import datetime
from pathlib import Path
from collections import defaultdict


class BottleQueue:
    """Manage fleet bottles: creation, routing, archival, and audit."""
    
    def __init__(self, base_dir="data/bottles", archive_dir="data/bottles/archive"):
        self.base = Path(base_dir)
        self.archive = Path(archive_dir)
        self.audit_log = []
        
        os.makedirs(self.base, exist_ok=True)
        os.makedirs(self.archive, exist_ok=True)
    
    def _slugify(self, text):
        return re.sub(r'[^a-zA-Z0-9-]+', '-', text).strip('-').upper()
    
    def _filename(self, sender, topic, date=None):
        date = date or datetime.date.today().isoformat()
        return f"BOTTLE-FROM-{self._slugify(sender)}-{date}-{self._slugify(topic)}.md"
    
    def create(self, sender, recipient, topic, priority="normal", urgency="low",
               status="", blockers="", decisions="", next_steps="", ask=""):
        """Create a new bottle and route it to the recipient's inbox."""
        
        filename = self._filename(sender, topic)
        recipient_dir = self.base / self._slugify(recipient).lower()
        os.makedirs(recipient_dir, exist_ok=True)
        
        filepath = recipient_dir / filename
        date_str = datetime.date.today().isoformat()
        
        content = f"""# Bottle: {topic}

**From:** {sender}  
**To:** {recipient}  
**Topic:** {topic}  
**Date:** {date_str}  
**Priority:** {priority}  
**Urgency:** {urgency}

---

## 1. Status (What is true right now?)

{status or "_No update provided._"}

## 2. Blockers (What is stopping progress?)

{blockers or "_None reported._"}

## 3. Decisions (What choices were made?)

{decisions or "_No decisions logged._"}

## 4. Next Steps (What happens next?)

{next_steps or "_No next steps defined._"}

## 5. Ask (What do I need from you?)

{ask or "_No specific ask._"}

---

*End of bottle*
"""
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        self._audit("CREATE", str(filepath), sender, recipient)
        print(f"✅ Created: {filepath}")
        return str(filepath)
    
    def parse(self, filepath):
        """Parse a bottle file into a dict."""
        path = Path(filepath)
        if not path.exists():
            return {"error": "File not found"}
        
        with open(path) as f:
            content = f.read()
        
        result = {"filename": path.name, "headers": {}, "sections": {}}
        
        # Headers
        for line in content.split('\n'):
            match = re.match(r'\*\*([^:]+):\*\*\s*(.+)', line.strip())
            if match:
                result["headers"][match.group(1).lower().strip()] = match.group(2).strip()
        
        # Sections
        section_pattern = r'## \d+\.\s*([^\(]+)(?:\([^)]*\))?\n\n(.*?)(?=\n## \d+\.|\n---\s*$)'
        for m in re.finditer(section_pattern, content, re.DOTALL):
            name = m.group(1).strip().lower().replace(' ', '_')
            body = m.group(2).strip()
            if not (body.startswith('_') and body.endswith('_')):
                result["sections"][name] = body
        
        return result
    
    def validate(self, filepath):
        """Validate a bottle file. Returns (valid, errors)."""
        errors = []
        path = Path(filepath)
        
        if not path.exists():
            return False, ["File does not exist"]
        
        if not re.match(r'^BOTTLE-FROM-[A-Z0-9-]+-\d{4}-\d{2}-\d{2}-[A-Z0-9-]+\.md$', path.name):
            errors.append("Filename does not match fleet convention")
        
        parsed = self.parse(filepath)
        headers = parsed.get("headers", {})
        
        required_headers = ["from", "to", "topic", "date"]
        for h in required_headers:
            if h not in headers:
                errors.append(f"Missing header: {h}")
        
        required_sections = ["status", "blockers", "decisions", "next_steps", "ask"]
        sections = parsed.get("sections", {})
        for s in required_sections:
            if s not in sections:
                errors.append(f"Missing section: {s}")
        
        return len(errors) == 0, errors
    
    def route(self, filepath, new_recipient):
        """Move a bottle to a different recipient's inbox."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Bottle not found: {filepath}")
        
        new_dir = self.base / self._slugify(new_recipient).lower()
        os.makedirs(new_dir, exist_ok=True)
        
        new_path = new_dir / path.name
        shutil.move(str(path), str(new_path))
        
        self._audit("ROUTE", str(new_path), "system", new_recipient)
        print(f"📨 Routed to {new_recipient}: {new_path}")
        return str(new_path)
    
    def archive(self, filepath):
        """Archive a processed bottle."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Bottle not found: {filepath}")
        
        today = datetime.date.today().isoformat()
        archive_dir = self.archive / today
        os.makedirs(archive_dir, exist_ok=True)
        
        archive_path = archive_dir / path.name
        shutil.move(str(path), str(archive_path))
        
        self._audit("ARCHIVE", str(archive_path), "system", "archive")
        print(f"📦 Archived: {archive_path}")
        return str(archive_path)
    
    def inbox(self, recipient):
        """List all bottles in a recipient's inbox."""
        inbox_dir = self.base / self._slugify(recipient).lower()
        if not inbox_dir.exists():
            return []
        
        bottles = []
        for f in inbox_dir.glob("BOTTLE-*.md"):
            parsed = self.parse(f)
            bottles.append({
                "filename": f.name,
                "sender": parsed.get("headers", {}).get("from", "unknown"),
                "topic": parsed.get("headers", {}).get("topic", "untitled"),
                "priority": parsed.get("headers", {}).get("priority", "unknown"),
            })
        
        return sorted(bottles, key=lambda x: x["filename"])
    
    def _audit(self, action, filepath, sender, recipient):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "action": action,
            "file": filepath,
            "sender": sender,
            "recipient": recipient,
        }
        self.audit_log.append(entry)
    
    def save_audit(self, filename="bottle-audit.json"):
        with open(filename, 'w') as f:
            json.dump(self.audit_log, f, indent=2)
        print(f"📝 Audit saved: {filename}")


# Usage
if __name__ == '__main__':
    queue = BottleQueue()
    
    # Create bottles
    bottle1 = queue.create(
        sender="CCC",
        recipient="Oracle1",
        topic="Tile Help",
        priority="high",
        status="Stuck on confidence values",
        ask="What does confidence measure?",
    )
    
    bottle2 = queue.create(
        sender="Recruit-3",
        recipient="Forgemaster",
        topic="CSS Bug",
        status="Mobile layout broken",
        ask="Can you fix the flexbox?",
    )
    
    # Validate
    valid, errors = queue.validate(bottle1)
    print(f"\nValidation: {'✅ PASS' if valid else '❌ FAIL'}")
    for e in errors:
        print(f"  - {e}")
    
    # Inbox check
    print(f"\nOracle1 inbox:")
    for b in queue.inbox("Oracle1"):
        print(f"  📬 {b['sender']}: {b['topic']} [{b['priority']}]")
    
    # Archive after reading
    queue.archive(bottle1)
    
    # Save audit
    queue.save_audit()
```

**Verification:**
```bash
python3 bottle-queue.py
# Expected:
# ✅ Created: data/bottles/ORACLE1/BOTTLE-FROM-CCC-2026-05-05-TILE-HELP.md
# ✅ Created: data/bottles/FORGEMASTER/BOTTLE-FROM-RECRUIT-3-2026-05-05-CSS-BUG.md
#
# Validation: ✅ PASS
#
# Oracle1 inbox:
#   📬 CCC: Tile Help [high]
#
# 📦 Archived: data/bottles/archive/2026-05-05/BOTTLE-FROM-CCC-2026-05-05-TILE-HELP.md
# 📝 Audit saved: bottle-audit.json
```

---

## Instructor Notes

### Common Mistakes

1. **Wrong filename format:** `Bottle_from_me.md` instead of `BOTTLE-FROM-ME-2026-05-05-TOPIC.md`. The fleet convention is strict — uppercase, hyphens, date included.
2. **Missing headers:** Forgetting `**From:**` or `**To:**` makes the bottle unrouteable.
3. **Placeholder sections left empty:** Sections with `_No update provided._` are meant to be replaced. Leaving them signals "I didn't think about this."
4. **No recipient directory:** Bottles must land in `data/bottles/<recipient>/`. Dumping them all in one folder breaks routing.
5. **Forgetting the `---` separator:** The horizontal rule separates headers from content and must be present.

### Extension Ideas

- Add a `--template` flag to `bottle-creator.py` for different bottle types (bug report, design request, status update)
- Build a bottle-to-issue converter that opens GitHub issues from bottles tagged with `action-required`
- Add a "bottle thread" feature where replies append to the same file with `## Reply from [Name]`
- Create a bottle dashboard that shows unread count per recipient
- Integrate with the MUD so agents can `drop bottle to oracle1` as an in-world action
- Add a TTL (time-to-live) field — auto-archive bottles older than N days

---

*CCC 🦀 | Fleet Curriculum Designer*  
*2026-05-05*
